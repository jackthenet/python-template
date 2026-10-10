# Questions: map-default-drop-shift

One question file per change, created at **P.1 Frame** from this template and named `<change-name>.md`. It replaces the retired central `AI_Questions.md` (archived at `docs/questions/archive-AI_Questions.md`).

- **Change:** map-default-drop-shift (ISSUE — may need a Spec Amendment to `docs/specs/structure-map.md` first)
- **TODO file:** `docs/todo/map-default-drop-shift.md`
- **Spec:** n/a (defect against `docs/specs/structure-map.md` REQ-014 / AC-014)
- **Opened:** 2026-10-09
- **Status:** ALL ANSWERED  <!-- OPEN | ALL ANSWERED -->
- **Answer rounds:** 4 (2026-10-09) — **all 19 questions ANSWERED and incorporated** (Q-1..Q-19; Q-19 derived from Q-15's answer)

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

P.2 Interrogate ran 2026-10-09 (18 entries below); P.3 Answer presented them in 4 rounds on 2026-10-09 and every entry is now `ANSWERED` + `incorporated`. Q-19 was derived from the answer to Q-15 and answered in the same batch (round 4). The five `**Blocking:** yes` entries (Q-1..Q-5) were asked in round 1.

**Evidence gathered by P.2** (read-only inspection of `feature/structure-map`, PR #75, PR #76):

- `scripts/make_map.py:74` `_DEFAULT_MAX_CHARS = 20`; `:375-386` `_drop_long_defaults` (`args.defaults = [d for d in args.defaults if len(ast.unparse(d)) <= _DEFAULT_MAX_CHARS]`); called from `_signature` at `:396`.
- Spec: REQ-014 (`docs/specs/structure-map.md:287-289`) — "a parameter default is included **only when its unparsed text is ≤ 20 characters**"; AC-014 (`:424`) — "the signature text equals the `ast.unparse` rendering … a parameter default of ≤ 20 characters is shown while a longer one is omitted". No REQ/AC/INV/EDGE anywhere states that the rendered parameter list must stay grammatically valid or call-compatible.
- The rule was chosen in `docs/questions/structure-map.md` **Q-27** ("defaults included when short (≤ 20 chars), omitted otherwise"); the positional-alignment consequence was never asked, so it was never decided.
- **The defect is already live in the committed artifact**, not merely reachable: `tests/mail_test_helpers.py:70` is `simple_template(name='test', subject='Test {{who}}', body_html='<p>Test {{who}}</p>', body_text='Test {{who}}')` (default lengths 6/14/21/14). PR #75's `STRUCTURE.md:1813` renders `simple_template(name: str, subject: str='test', body_html: str='Test {{who}}', body_text: str='Test {{who}}')` — `name` looks required, `body_html`'s default is wrong. AC-021 byte-compares that file.
- Scan of the 895 functions in Packages scope (`src`, `scripts`, `migrations`, `tests/conftest.py`, `tests/*_test_helpers.py`) at PR #75's tree: **exactly one** function has a >20-character positional default (`simple_template`); no function has a single too-long positional default.
- AC-014's unit witnesses do not cover the shift: `tests/unit/test_make_map.py:654 _AC014_LINES` and `:672 _AC014_DEFAULTS` put every long default in `kw_defaults` except `items(pool: list[int]=[1, 2, 3, 4, 5, 6, 7])`, which is its function's **only** default.
- Gates that actually apply to `scripts/make_map.py`: `ruff check .` (lint.yml covers `scripts/`), `uv run mypy scripts/` (REQ-025), the local `structure-map-check` pre-commit hook (REQ-023, `files: \.py$`, check-only), and **no** CI job runs `make_map.py --check` (REQ-023/REQ-026). `complexipy` runs on `src tests` only (`.github/workflows/quality.yml:146`) — the TODO's "complexipy applies to `scripts/`" constraint is inaccurate. PR #76 (**merged into `main` at `2ab0461` while P.2 ran**) added ruff rule `D` with `"scripts/*" = ["D"]` in `[tool.ruff.lint.per-file-ignores]`, so the edited `_drop_long_defaults` docstring is not D-gated.
- **PR status at P.2 time:** #76 merged; **#75 (`feature/structure-map`) is the only open PR** — `scripts/make_map.py` and `STRUCTURE.md` still exist only on that branch.

**State change after P.2, recorded at P.3 (2026-10-09).** PR #75 **merged into `main`** at 2026-10-09T20:09:53Z (merge commit `7dfaa23`); before merging it had already merged post-#76 `main` and regenerated `STRUCTURE.md` (`3673e28`). `scripts/make_map.py` and `STRUCTURE.md` therefore now exist on `main` (version `1.1.0`) and the defective line is still live there (`STRUCTURE.md:1813` renders `simple_template(name: str, subject: str='test', body_html: str='Test {{who}}', body_text: str='Test {{who}}')`). Consequence: a reproduction test can be written and RED observed on a branch cut from `main`, and **Q-3 / Q-4 / Q-13 are settled by facts** rather than by choice.

## Q-1 — Is the shifted rendering a defect against the approved spec, or behavior the spec never stated?
- **Step:** P.2 Interrogate
- **Blocking:** yes
- **Why needed:** It fixes the change type and therefore the whole phase set. An ISSUE must be "a deviation from approved spec behavior"; if the required behavior is not stated, AGENTS requires a Spec Amendment PR (or reclassification as FEATURE).
- **Context:** Read literally, the current output **satisfies** AC-014: the signature text *is* an `ast.unparse` rendering — of the `ast.arguments` node that `_drop_long_defaults` mutated — and the too-long default *is* omitted. REQ-014 says only "included only when its unparsed text is ≤ 20 characters"; nothing in REQ-014, AC-014, INV-001..006 or EDGE-001..016 requires the rendered parameter list to be valid Python or to mean the same call signature as the source. structure-map Q-27 chose the ≤ 20-char rule without ever considering positional alignment.
- **Question:** Does the approved spec already require a call-compatible signature (→ plain ISSUE, the amendment only clarifies wording), or is "the rendered signature must preserve which parameters have defaults" new behavior the spec never stated (→ Spec Amendment to REQ-014/AC-014 first, or reclassify as FEATURE per the Escalation Rules)? If amended: does it stay inside REQ-014/AC-014, or does it need new IDs (e.g. a new EDGE and/or INV)?
- **Answer:** **ISSUE + Spec Amendment first.** The approved spec does **not** state call-compatibility of the rendered parameter list (structure-map Q-27 chose the ≤ 20-char rule without considering positional alignment), so the required behavior must be written into the spec before it is fixed: open a **Spec Amendment PR** against `docs/specs/structure-map.md` (REQ-014 / AC-014, `## Changelog` v2 entry), merge it, then run this change as an **ISSUE** (patch bump). Not a plain ISSUE (that would edit an approved spec outside the amendment workflow) and not a FEATURE (no new capability).
- **Date:** 2026-10-09
- **Status:** ANSWERED
- **Incorporated:** yes — change type fixed (ISSUE, amendment-first); drives Q-9 (whether the rule gets new IDs inside REQ-014/AC-014 or an `INV`/`EDGE`) and Q-17 (patch bump)

## Q-2 — Which rendering is required when a positional default is too long?
- **Step:** P.2 Interrogate
- **Blocking:** yes
- **Why needed:** The fix's whole content, the amended AC-014 wording, and every witness depend on it; the alternatives are not equivalent and one of them is impossible.
- **Context:** `args.defaults` is one list aligned to the **tail** of `posonlyargs + args`, so removing an entry shifts the kept defaults onto earlier parameters; `args.kw_defaults` aligns one-to-one with `kwonlyargs`, so a dropped keyword-only default simply renders with no default (legal). Candidates: **(a)** keep every default in position and abbreviate the long one with a placeholder (`body_html: str=…` or `=...`); **(b)** once any positional default is too long, render **no** positional defaults for that function (`simple_template(name: str, subject: str, body_html: str, body_text: str)`); **(c)** keep today's list-drop and instead document that the map is a simplification, not a call signature; **(d)** something else. Note "drop only the offending entry, keep the others in place" is not expressible — it puts a non-default parameter before defaulted ones, which is invalid Python.
- **Question:** Which of (a)/(b)/(c)/(d) is normative? If a placeholder is used, which token — `…` (the character REQ-017/REQ-018 already use for elision) or `...`? Must the reader be able to tell that a value was abbreviated?
- **Answer:** **(a) Placeholder in position.** Every default keeps its slot; an over-long default is rendered as a placeholder instead of being removed from the list, so the parameter list stays grammatically valid **and** keeps optionality visible. Token: `…` — the same character REQ-017/REQ-018 already use for elision (no new token, no `...`). The reader must be able to tell a value was abbreviated: `body_html: str=…` says "has a default, too long to show".
  Target rendering for the live witness: `def simple_template(name: str='test', subject: str='Test {{who}}', body_html: str=…, body_text: str='Test {{who}}') -> EmailTemplate`
- **Date:** 2026-10-09
- **Status:** ANSWERED
- **Incorporated:** yes — normative rendering for the amended REQ-014/AC-014; fixes the expected line in the reproduction test (Q-10) and the rewritten `_AC014_LINES`/`_AC014_DEFAULTS` witnesses (Q-11)

## Q-3 — Fix inside open PR #75, or after `structure-map` merges?
- **Step:** P.2 Interrogate
- **Blocking:** yes
- **Why needed:** `scripts/make_map.py` does not exist on `main` — the reproduction test cannot be written, and no RED can be observed, until the code exists. The choice also decides whether `main` ships a wrong signature in the meantime.
- **Context:** The TODO says `Depends on: structure-map (must merge first)` and that "the witness set does not cover this case". The second half is only true of the AC-014 **unit fixture**: the committed `STRUCTURE.md:1813` in PR #75 already exhibits the shift, so the wrong line is inside the artifact AC-021 byte-compares and the local hook checks. PR #75 is otherwise at S6.4 (review report clean, Phase 5 gate passed).
- **Question:** (a) amend PR #75 before it merges so the defect never reaches `main` — but structure-map may not introduce behavior its approved spec does not state, so the spec on `main` would have to be amended first (see Q-4); or (b) merge #75 as-is and fix it afterwards as a separate ISSUE, accepting that `main` carries the misleading `simple_template` signature until then? Which does the user want, and does the answer change the change type (amendment + ISSUE vs amendment + a finding closed inside #75)?
- **Answer:** **Settled by facts, not by choice — after the merge.** PR #75 merged at 2026-10-09T20:09:53Z (`7dfaa23`) while this change was being prepared, so option (a) (amend #75 before it merges) is no longer available. The fix is a **separate ISSUE change on a branch cut from `main`**, preceded by the Spec Amendment PR per Q-1. `main` carries the misleading `simple_template` signature until this change lands; the user accepted that by choosing the amendment-first shape (Q-17).
- **Date:** 2026-10-09
- **Status:** ANSWERED
- **Incorporated:** yes — worktree/branch will be cut from `main` at P.4; `Depends on: structure-map` is satisfied (`7dfaa23` reachable from `origin/main`)

## Q-4 — Spec Amendment mechanics, and what the amendment does to open PR #75
- **Step:** P.2 Interrogate
- **Blocking:** yes
- **Why needed:** AGENTS forbids editing an approved spec outside the Spec Amendment Workflow, and the amendment's timing determines whether PR #75's already-GREEN witnesses become stale.
- **Context:** `docs/specs/structure-map.md` is already on `main` (commits `f9e4eea`, `8eb130b`); PR #75's file list does **not** include the spec file. The amendment workflow requires: a new PR, a `## Changelog` v2 entry at the top, identification of affected tasks (any task citing the changed REQ/AC), re-derived tests + RED/GREEN for them, a matrix update, and the spec PR merged **before** implementation resumes. structure-map's T-004 owns AC-014; T-005/T-006 own the committed map (AC-021).
- **Question:** Open the amendment PR now (then PR #75's `_AC014_LINES`/`_AC014_DEFAULTS` witnesses and its committed `STRUCTURE.md` no longer match the amended spec and must be updated on that branch before it merges), or amend only after #75 merges (then the amendment is a normal follow-up PR and this change re-derives its tests)? Which tasks does the user count as "affected tasks" for step 4 of the amendment workflow?
- **Answer:** **Amendment PR first, merged before implementation resumes.** PR A touches only `docs/specs/structure-map.md` (Changelog v2, no version bump). PR B (`issue/map-default-drop-shift`) then re-derives the witnesses and fixes the code. **Affected tasks:** T-004 (owns AC-014 — its `_AC014_LINES` / `_AC014_DEFAULTS` witnesses are re-derived from the amended AC) and T-005/T-006 (own the committed map, AC-021 — regenerated). Because PR #75 is already merged and its tasks are `VERIFIED`, the re-derivation is **not** performed on that branch; it happens inside PR B, which is the amendment workflow's step-4 re-run for this change.
- **Date:** 2026-10-09
- **Status:** ANSWERED
- **Incorporated:** yes — PR shape fixed (see Q-17); the amendment's affected-task list recorded for the triage record

## Q-5 — Value-triage decision: implement, merge into another change, or drop?
- **Step:** P.2 Interrogate
- **Blocking:** yes
- **Why needed:** AGENTS prohibits P.4 (branch + worktree) for a TODO whose value-triage decision is not recorded; the TODO's `Decision:` is still `PENDING`.
- **Context:** TODO `## Value triage`: score **2/5**, recommendation "implement — after `structure-map` merges, as a light-tier ISSUE; open the Spec Amendment PR first if the triage shows REQ-014 does not already settle the required rendering". P.2 confirms the rendering is **not** settled by REQ-014 (Q-1) and that the defect is already visible in the committed map, which raises the value above the "currently unwitnessed" premise the score was based on.
- **Question:** Confirm **implement** (and at which point in the #75/#76 order from Q-3/Q-13), or merge this into PR #75, or drop? If the score should be re-rated now that a live witness exists, say so.
- **Answer:** **Implement — re-rated 2/5 → 3/5.** The original score rested on the premise that the defect was unwitnessed; P.2 found it live in the committed `STRUCTURE.md` on `main`, which raises the value. Not merged into another change (#75 and #76 are both merged), not dropped.
- **Date:** 2026-10-09
- **Status:** ANSWERED
- **Incorporated:** yes — `docs/todo/map-default-drop-shift.md` `## Value triage` score + Decision; the P.4 gate (branch + worktree) is now open

## Q-6 — Is the "only default of the function" case in scope?
- **Step:** P.2 Interrogate
- **Why needed:** Same root cause, different symptom, and it decides how wide the amended rule and the test set are.
- **Context:** When the too-long default is a function's **only** positional default, the current code renders that parameter as required: `_AC014_LINES` pins `- def \`items(pool: list[int]) -> None\`` for a source parameter `pool: list[int]=[1, 2, 3, 4, 5, 6, 7]`. The map then understates optionality even though nothing shifts. My scan found no such function in the repository today, so this case is real but unwitnessed in the committed map.
- **Question:** Must the fix also keep "this parameter is optional" visible in that case, or is the scope strictly the shift (defaults landing on the wrong parameters)?
- **Answer:** **In scope.** The placeholder rule (Q-2) keeps the slot, so `items(pool: list[int]=[1, 2, 3, 4, 5, 6, 7])` renders as `items(pool: list[int]=…) -> None` — optionality stays visible instead of the parameter looking required. The amended AC-014 witness is rewritten to that expectation rather than loosened.
- **Date:** 2026-10-09
- **Status:** ANSWERED
- **Incorporated:** yes — part of the amended REQ-014/AC-014 + EDGE-017 wording; the `_AC014_LINES` expectation for `items(...)` changes (see Q-11)

## Q-7 — Keyword-only and positional-only parameters: same rule or not?
- **Step:** P.2 Interrogate
- **Why needed:** The two branches of `_drop_long_defaults` behave differently today; an amendment that fixes only one leaves a sibling inconsistency, and the fix's size depends on the answer.
- **Context:** `args.kw_defaults` handling (`scripts/make_map.py:383-386`) replaces a long default with `None`, which renders the keyword-only parameter with no default — grammatically valid, but it also hides that the parameter is optional (AC-014's fixture puts all its long defaults here, which is why the witnesses pass). `args.defaults` covers `posonlyargs + args` **jointly**, so a positional-only long default shifts the kept defaults onto earlier parameters exactly like a positional one.
- **Question:** Does the amended rule treat keyword-only and positional-only defaults by the same principle as positional ones (consistent abbreviation), or is "valid but optionality hidden" acceptable for keyword-only parameters? Explicitly: is a positional-only parameter covered by the fix?
- **Answer:** **Uniform placeholder for all three.** One principle, one helper: an over-long default renders as `name: T=…` **in its own slot** whether it sits in `args.defaults` (positional or positional-only) or `args.kw_defaults` (keyword-only). The `kw_defaults` branch's current "replace with `None`" rendering — valid Python but optionality hidden — is fixed by the same rule, so no sibling inconsistency remains.
  - posonly/positional: `f(a: int, b: str='x')` → `f(a: int=…, b: str='x')`
  - positional-only: `f(a: int, /)` → `f(a: int=…, /)`
  - keyword-only: `f(*, flag: int)` → `f(*, flag: int=…)`
- **Date:** 2026-10-09
- **Status:** ANSWERED
- **Incorporated:** yes — the amended rule covers `args.defaults` (posonly + positional) and `args.kw_defaults` identically; both branches of `_drop_long_defaults` are in the fix scope

## Q-8 — Is the 20-character threshold itself open for reconsideration?
- **Step:** P.2 Interrogate
- **Why needed:** The TODO makes the threshold out of scope "unless the triage shows the shift is only reachable through it" — the triage shows exactly that, so the exclusion condition has triggered and needs a decision.
- **Context:** A default is dropped only when its `ast.unparse` text exceeds `_DEFAULT_MAX_CHARS = 20` (`scripts/make_map.py:74`). Raising it to 21 would make the repository's only witness (`simple_template`, 21-char default) disappear from the committed map with a one-line change — but the alignment bug would remain and would return for the next 22-character default. The threshold is a module constant, not a CLI option (REQ-002's six options do not include it).
- **Question:** Keep 20 and fix the alignment (P.2's recommendation), or also revisit the threshold — and is raising the threshold acceptable as *any* part of the fix, or is it suppression and therefore out of scope? Should the threshold become configurable (P.2 recommends no)?
- **Answer:** **Keep 20; fix the alignment only.** `_DEFAULT_MAX_CHARS = 20` (`scripts/make_map.py:74`) is untouched. Raising it to 21 would make the repository's only witness disappear from the map (the `body_html` default is exactly 21 chars) while the alignment bug stayed in the code and returned for the next 22-character default — suppression, not a fix. Not configurable either (no new CLI option / setting, which would also break the light-tier qualification).
- **Date:** 2026-10-09
- **Status:** ANSWERED
- **Incorporated:** yes — the threshold stays out of scope; the fix is confined to the drop rule's alignment handling

## Q-9 — New invariant/edge ID and a property test, or one unit witness?
- **Step:** P.2 Interrogate
- **Why needed:** AGENTS Phase 3 requires a Hypothesis property test for every `INV-XXX`, and Phase 5 requires spec coverage = 100%; whether an INV is created changes the required test set and the light-tier eligibility.
- **Context:** structure-map's `tests/property/test_structure_map.py` witnesses INV-001..006 only. A durable rule would be an invariant of the form "the rendered parameter list parses, and its parameter names, order and which-parameters-have-defaults set match the source signature, except that an over-long default value is abbreviated". The spec's Edge Cases table (EDGE-001..016) has no entry for an over-long default at all.
- **Question:** Does the amendment add an `INV-007` (and an `EDGE-017`) for signature fidelity — in which case a property test over generated signatures is mandatory — or is the rule expressed inside REQ-014/AC-014 with a single unit witness plus the regenerated map?
- **Answer:** **Add `INV-007` + `EDGE-017`.** The Spec Amendment (v2 of `docs/specs/structure-map.md`) reads:
  - **REQ-014** — a default is shown only when its unparsed text is ≤ 20 characters; an over-long default is rendered as `…` **in its own slot** (never removed from the list).
  - **AC-014** — the rendered parameter list is valid Python and preserves parameter names, order, and which parameters have defaults.
  - **INV-007** (signature fidelity) — parsing the rendered parameter list yields the same parameter structure as the source signature (names, order, defaults-set); only default *values* may be abbreviated.
  - **EDGE-017** — an over-long default in a positional / positional-only / keyword-only slot.
  Consequence: Phase 3 MUST write a **Hypothesis property test** for INV-007 in `tests/property/test_structure_map.py` (generated signatures), and `scripts/check_traceability.py` requires a matrix row for each new ID (see Q-14).
- **Date:** 2026-10-09
- **Status:** ANSWERED
- **Incorporated:** yes — new spec IDs and the property-test obligation are fixed for PR A (spec) and Phase 3 (test)

## Q-10 — Reproduction witness: the real committed map line, or a synthetic fixture?
- **Step:** P.2 Interrogate
- **Why needed:** Phase 3 for an ISSUE requires a failing reproduction test; the choice fixes the test category, the traceability row, and whether the test is meaningful before the map is regenerated.
- **Context:** Two candidate witnesses: **(a)** the real one — assert the `simple_template` line in the committed `STRUCTURE.md` (acceptance-level, fails today at PR #75's commit, and is exactly what AC-021 protects); **(b)** a synthetic fixture in `tests/unit/test_make_map.py` next to `_AC014_MODULE` (fast, isolated, but a new fixture rather than the artifact that is actually wrong). Note `tests/mail_test_helpers.py` is itself Packages-scope (REQ-011), so changing that helper would itself change the map.
- **Question:** Which witness — (a), (b), or both — and in which file (`tests/acceptance/test_structure_map.py` vs `tests/unit/test_make_map.py`)? May the reproduction test assert on the committed `STRUCTURE.md` bytes, or must it render into a temp dir?
- **Answer:** **Both.**
  1. `tests/unit/test_make_map.py` — synthetic fixture: a function with a 21-character positional default plus a short one; expects `def f(a: int=…, b: str='x') -> None`, fails today with `def f(a: int, b: str='x')`. Pins the rule in isolation.
  2. `tests/acceptance/test_structure_map.py` — asserts the real `simple_template` line of the **committed** `STRUCTURE.md` renders with `body_html: str=…`; fails today at `main`'s committed bytes. Pins that the shipped artifact is actually correct (the same artifact AC-021 byte-compares).
  Asserting on the committed `STRUCTURE.md` is allowed (AC-021's existing test already does exactly that); the rule fixture renders into a temp dir.
- **Date:** 2026-10-09
- **Status:** ANSWERED
- **Incorporated:** yes — Phase 3 test set: one unit reproduction test + one acceptance reproduction test (+ the INV-007 property test from Q-9)

## Q-11 — Are the existing AC-014 witnesses allowed to change?
- **Step:** P.2 Interrogate
- **Why needed:** The no-weakening prohibition and "tests are the contract" both bite here; without an explicit answer the implementing step cannot tell a required re-derivation from a forbidden weakening.
- **Context:** `tests/unit/test_make_map.py:654 _AC014_LINES` pins `- def \`items(pool: list[int]) -> None\`` and `:672 _AC014_DEFAULTS` pins the needle `("[1, 2, 3, 4, 5, 6, 7]", False)` ("21 characters, positional: omitted"). A placeholder-style fix changes both; a drop-all-positional-defaults style changes the `resize(...)` line's rendering of `step`/`exact`. AGENTS forbids weakening or deleting a test to reach GREEN and resolves spec/test conflicts through the amendment, never by editing the test.
- **Question:** Confirm that the amendment authorizes exactly these witness edits as re-derivation from the amended AC-014 (needle replaced, not removed; expected line list rewritten, not loosened), and that no clause of AC-014 may be dropped from the test in the process.
- **Answer:** **Authorized — re-derivation, not weakening.** The amendment explicitly authorizes rewriting the two existing AC-014 fixtures to the stricter expectation:
  - `_AC014_LINES`: `- def \`items(pool: list[int]) -> None\`` → `- def \`items(pool: list[int]=…) -> None\``
  - `_AC014_DEFAULTS`: the `("[1, 2, 3, 4, 5, 6, 7]", False)` needle stays (the long value is still absent from the output) **and** a positive assertion for `pool: list[int]=…` is added.
  - The `resize(...)` line is unaffected (`step` / `exact` defaults are both ≤ 20 chars).
  No clause of AC-014 may be dropped; the needle is replaced, not removed, and the assertion set only grows.
- **Date:** 2026-10-09
- **Status:** ANSWERED
- **Incorporated:** yes — recorded in the triage record as the authorized witness edits, so Phase 4 can tell re-derivation from forbidden weakening

## Q-12 — Light-tier ISSUE or full Phase 5?
- **Step:** P.2 Interrogate
- **Why needed:** The light tier changes Phase 5 (targeted + smoke instead of full regression, with the full suite moved to the S6.4 pre-merge gate) and must be qualified in the triage record.
- **Context:** Light tier requires: single feature, ≤ 3 files touched **excluding tests**, no new dependency, no new public interface, no cross-feature change, and existing tests covering the area (named in the triage). Here the touched non-test files are `scripts/make_map.py` and the regenerated `STRUCTURE.md` (required by REQ-021/REQ-027 and the `structure-map-check` hook), plus `docs/specs/structure-map.md` if the amendment is a separate PR. The covering tests are `test_ac_014_symbol_inventory_and_unparsed_signatures` and `test_ac_021_committed_map_matches_fresh_render`.
- **Question:** Does the generated `STRUCTURE.md` count toward the ≤ 3 files, and does the spec file count when it is amended in a separate PR? Is the light tier approved, or full Phase 5 (acceptance + property + contract + coverage + spec coverage 100%)?
- **Answer:** **Light tier approved.** Non-test files touched by PR B = **2**: `scripts/make_map.py` (the fix) and `STRUCTURE.md` (regenerated — required by AC-021 and the `structure-map-check` hook, so it counts but stays within the ≤ 3 budget). The spec file does **not** count — it is amended in PR A, a separate PR. Criteria all hold: single feature, ≤ 3 non-test files, no new dependency, no new public interface, no cross-feature change, covering tests named (`test_ac_014_symbol_inventory_and_unparsed_signatures`, `test_ac_021_committed_map_matches_fresh_render`).
  → Phase 5 runs **targeted + smoke**: the reproduction tests, the two covering tests, the INV-007 property test, `uv run pytest tests/acceptance tests/unit tests/property -v` for the affected area, plus `ruff check <changed-paths>` and `uv run mypy scripts/`. The **full regression suite** runs as the **S6.4 pre-merge gate** and must pass; the result is recorded in the review report. Qualification recorded in the triage record (`docs/verification/map-default-drop-shift.md`).
- **Date:** 2026-10-09
- **Status:** ANSWERED
- **Incorporated:** yes — Phase 5 tier fixed (light), covering tests named in the triage record

## Q-13 — Regeneration and merge order across PR #75, PR #76 and this change
- **Step:** P.2 Interrogate
- **Why needed:** #76 merged while P.2 ran, which creates a stale-map problem that lands on whichever change touches `STRUCTURE.md` next — possibly this one. The order decides who regenerates what and where conflicts land.
- **Context:** PR #75 adds `STRUCTURE.md`, the `structure-map-check` pre-commit hook (`files: \.py$`, check-only) and the map skill; its committed map was generated from a tree that **predates** #76. PR #76 (`chore/ruff-d-docstrings`) is now **merged** (`2ab0461`) and rewrote docstrings in 40+ `src/` modules — those docstrings **are** the map's summary text (REQ-018) — but it touched no `STRUCTURE.md` (none existed on its base). So as soon as #75 merges, `make_map.py --check` exits `1` on `main` and the new local hook fails on the next `.py` commit, and `main` needs a regeneration commit — which cannot be a direct-to-`main` commit (only `docs/todo/` and `docs/questions/` may go there). This ISSUE regenerates the map again on top of that. REQ-022's rule: on a conflict in `STRUCTURE.md`, take either side and regenerate — never hand-merge.
- **Question:** Should PR #75 rebase onto the post-#76 `main` and regenerate `STRUCTURE.md` before it merges (P.2's recommendation — it makes the map correct at merge), or is a separate small change opened afterwards to regenerate it? Should this change be sequenced strictly after that regeneration, and does the regeneration belong in this change's PR if nobody else does it?
- **Answer:** **Resolved by PR #75 itself.** #75 merged post-#76 `main` and regenerated `STRUCTURE.md` in `3673e28` before merging, so the stale-map problem P.2 predicted never landed on `main`. This change regenerates the map once more, inside its own PR B, because its fix changes the rendered line (AC-021 + the `structure-map-check` hook require it). REQ-022's conflict rule (take either side, regenerate, never hand-merge) still applies if `main` moves again before PR B merges.
- **Date:** 2026-10-09
- **Status:** ANSWERED
- **Incorporated:** yes — regeneration is in scope for PR B; no separate regeneration change is needed

## Q-14 — How are the traceability rows written when the IDs collide?
- **Step:** P.2 Interrogate
- **Why needed:** Phase 5 must update the matrix and CI (`scripts/check_traceability.py`) enforces referential integrity; a row that cites a renamed/removed test function fails CI, and an ambiguous row misleads the next change.
- **Context:** `docs/verification/traceability.md` has no spec column, and `REQ-014`/`AC-014` rows already exist for other specs (lines 31, 102, 193, 276, 347) — structure-map's own rows are added by PR #75 (e.g. line 1041 for AC-021) and disambiguated only by the change name inside the Status cell. structure-map's P.5 record (finding 2) notes the checker treats REQ/AC IDs as one global namespace, so a structure-map ID can be "satisfied" by another spec's row.
- **Question:** Should this change add/update rows in the same bare-ID style with `map-default-drop-shift` named inside the cell, and must the new reproduction test's function name be added to the AC-014 row (or to a new amended AC ID)? If the amendment introduces `EDGE-017`/`INV-007`, is a row required for each (the checker fails a defined ID with no row)?
- **Answer:** **Bare-ID rows + new rows for the new IDs.** Update the structure-map `REQ-014` / `AC-014` rows to cite the re-derived witnesses, and add a row for **each** of `INV-007` and `EDGE-017` (`scripts/check_traceability.py` fails a defined ID with no matrix row). Each Status cell names `map-default-drop-shift` + the date inside the cell, per the historical-gate convention (decision Q-129); rows cite the new test function names (unit repro, acceptance repro, INV-007 property test). The global-namespace weakness P.5 flagged is **not** addressed here.
- **Date:** 2026-10-09
- **Status:** ANSWERED
- **Incorporated:** yes — Phase 5 S5.3 matrix work fixed: 2 updated rows + 2 new rows

## Q-15 — Which quality gates actually apply, and is the TODO's complexipy constraint wrong?
- **Step:** P.2 Interrogate
- **Why needed:** The TODO records a constraint that does not exist; the fix's evidence set must match the real gates, and the after-workflow-optimization reads the TODO.
- **Context:** The TODO says "complexipy `max-complexity-allowed = 15` applies to `scripts/` via the CI job added by structure-map T-001". CI actually runs `uv run complexipy src tests --max-complexity-allowed 15` (`.github/workflows/quality.yml:146`) — `scripts/` is not analyzed, and structure-map Q-28 settled exactly that. What does apply to `scripts/make_map.py`: `ruff check .` (lint.yml covers `scripts/`), `uv run mypy scripts/` (added by REQ-025), and the local `structure-map-check` hook; no CI job runs `make_map.py --check` (REQ-023/REQ-026). PR #76 (merged) added ruff rule `D` but per-file-ignores `scripts/*`, so the edited `_drop_long_defaults` docstring is not D-gated.
- **Question:** Confirm the gate set for this change (ruff on changed paths, `mypy scripts/`, targeted tests, full suite at Phase 5 or the S6.4 pre-merge gate). Should the complexipy ceiling be extended to `scripts/` as part of this change (P.2 recommends no — out of scope), and should the TODO's constraint line be corrected?
- **Answer:** **Gate set confirmed; and yes — extend complexipy to `scripts/`** (the user chose the option over P.2's "out of scope" recommendation). Gate set for PR B: `ruff check <changed-paths>` at each writing step + the whole-repo `ruff check .` sweep at Phase 5, `uv run mypy scripts/`, targeted tests in Phase 3/4, full regression at the S6.4 pre-merge gate (light tier, Q-12).
  **Follow-up needed (Q-19):** where the complexipy extension lands. Measured at `7dfaa23` (`uv run complexipy scripts --max-complexity-allowed 15`): `make_map.py` is clean (max 12; `_drop_long_defaults` = 6), but **4 pre-existing functions in 3 other files fail**: `check_traceability.py::check` 17, `check_traceability.py::matrix_rows` 19, `validate_task_dag.py::check_acyclic` 22, `verify_spec.py::main` 22. Extending the CI invocation in PR B therefore forces refactoring 4 unrelated functions (breaking the light-tier ≤ 3 non-test-file budget) or a config carve-out.
  The TODO's inaccurate constraint line ("complexipy … applies to `scripts/`") is corrected in the TODO record: CI runs `uv run complexipy src tests --max-complexity-allowed 15` (`.github/workflows/quality.yml:146`) — `scripts/` is not analyzed today.
- **Date:** 2026-10-09
- **Status:** ANSWERED
- **Incorporated:** yes — gates fixed for the triage record; the extension decision is carried to **Q-19** (late question, same batch) before P.4

## Q-16 — Is the fix confined to the parameter-default rule, or does it extend to other renderings?
- **Step:** P.2 Interrogate
- **Why needed:** It sets the scope boundary the Phase 6 review checks against, and prevents an unrequested drive-by fix in the same function family.
- **Context:** `_signature` → `_drop_long_defaults` is the only default-shortening path. Adjacent, related-but-different behaviors exist and were deliberately left alone by structure-map S4.3: `_class_name` renders class bases and keyword arguments with **no** length filter at all (`class C(metaclass=SomeVeryLongMetaclass)` renders in full), and it ignores a class's `type_params` (`class G[T](typing.Generic[T])` → `G(typing.Generic[T])`), recorded as "deliberately not changed". NFR-002's ≤ 2 000-line budget is unaffected (the fix changes line content, not line count), as are INV-001 determinism, INV-006 hook cleanliness, REQ-019 and REQ-020.
- **Question:** Is "no behavior change outside the parameter-default rule" the hard boundary — i.e. the class-header rendering and `type_params` stay untouched — or should the same abbreviation rule be applied there too?
- **Answer:** **Hard boundary: the parameter-default rule only.** `_class_name` keeps rendering class bases and keyword arguments in full (no length filter), and keeps ignoring `type_params` — structure-map S4.3 recorded both as deliberately not changed, and this change does not touch them. This is the boundary the Phase 6 review checks against (review check 6: no behavior beyond the type's contract).
- **Date:** 2026-10-09
- **Status:** ANSWERED
- **Incorporated:** yes — "Out of scope" section of `docs/todo/map-default-drop-shift.md` and the triage record's scope statement

## Q-17 — Version bump and PR shape
- **Step:** P.2 Interrogate
- **Why needed:** The bump level follows the change type (ISSUE → patch, FEATURE → minor), and the amendment is a separate PR; the base version depends on the merge order, so the shape must be agreed before S6.4.
- **Context:** AGENTS versioning: `bump-my-version bump <level>` at S6.4 with a clean tree, `tag = false`. PR #76 (DOCS/CHORE) merged with **no** version bump; PR #75 (FEATURE → minor) is still open, so the version this change bumps against depends on Q-3/Q-13. A Spec Amendment PR touching only `docs/specs/` would normally carry no bump.
- **Question:** Is the expected shape "one Spec Amendment PR (no bump) + one ISSUE PR (fix + regenerated map + tests, patch bump)", or does the amendment carry its own bump? If Q-1 lands as FEATURE/reclassification, is the bump then `minor`?
- **Answer:** **Two PRs: PR A (Spec Amendment) no bump; PR B (ISSUE) patch bump.** PR A touches only `docs/specs/` → no bump. PR B carries fix + regenerated map + tests and runs `bump-my-version bump patch` at S6.4 with a clean tree: **1.1.0 → 1.1.1** (version on `main` at P.4 time is `1.1.0`; PR #76 was a DOCS/CHORE and did not bump). No FEATURE reclassification, so no `minor`.
- **Date:** 2026-10-09
- **Status:** ANSWERED
- **Incorporated:** yes — S6.4 bump level fixed (patch); PR A carries no bump

## Q-18 — Is any backwards compatibility of map output required?
- **Step:** P.2 Interrogate
- **Why needed:** The fix changes the output of every invocation of the generator; whether an escape hatch is required is a scope decision, not an implementation detail.
- **Context:** REQ-002's six CLI options (`--root`, `--out`, `--check`, `--max-depth`, `--include-private`, `--help`) include nothing controlling the default rule, and REQ-019's determinism guarantee is about repeated runs over an unchanged tree, not about output stability across versions. The only consumer of the output is the committed `STRUCTURE.md` and the agents reading it via the `code-structure-map` skill (advisory only, REQ-026).
- **Question:** Is a compatibility option (a flag preserving the old rendering) or a documented one-time map change required, or is a single regenerated map plus a spec Changelog entry sufficient? P.2 recommends the latter.
- **Answer:** **Regenerated map + spec Changelog entry only.** No compatibility flag, no reader-note change to the `code-structure-map` skill or README. REQ-002's six options stay as they are; REQ-019's determinism guarantee is unaffected. The only consumers of the output are the committed `STRUCTURE.md` and agents reading it through the advisory skill (REQ-026).
- **Date:** 2026-10-09
- **Status:** ANSWERED
- **Incorporated:** yes — no CLI/interface change; PR B's file set stays `scripts/make_map.py` + `STRUCTURE.md` + tests + docs

## Q-19 — Where does the complexipy extension to `scripts/` land?
- **Step:** P.3 Answer (derived from the answer to Q-15, round 3)
- **Why needed:** The user chose to extend the cognitive-complexity ceiling to `scripts/`, but the extension does not pass today, so its placement decides whether PR B keeps the light tier (Q-12) and how many non-test files it touches.
- **Context:** Measured at `7dfaa23` with `uv run complexipy scripts --max-complexity-allowed 15`: `scripts/make_map.py` is clean (max 12; `_drop_long_defaults` = 6), but **4 pre-existing functions in 3 other files fail** — `check_traceability.py::check` 17, `check_traceability.py::matrix_rows` 19, `validate_task_dag.py::check_acyclic` 22, `verify_spec.py::main` 22. CI today runs `uv run complexipy src tests --max-complexity-allowed 15` (`.github/workflows/quality.yml:146`).
- **Question:** Extend the CI invocation inside PR B (forcing 4 unrelated refactors, ~6 non-test files, light tier lost), inside PR B with a config carve-out for the pre-existing offenders, or in a separate chore change?
- **Answer:** **Separate chore change.** PR B stays a light-tier ISSUE touching `scripts/make_map.py` + `STRUCTURE.md` (+ tests/docs). A new backlog change — `chore/complexipy-scripts` — extends the CI invocation to `src tests scripts` and refactors the 4 offenders, with full regression, no version bump, its own review. Its TODO is created at P.1 with its own value triage; the user's choice here is recorded as its decision.
- **Date:** 2026-10-09
- **Status:** ANSWERED
- **Incorporated:** yes — PR B's scope unchanged (light tier holds); `docs/todo/complexipy-scripts.md` opened as a new backlog item

## Late questions (Phases 2–6)

_none_
