# Questions: map-default-drop-shift

One question file per change, created at **P.1 Frame** from this template and named `<change-name>.md`. It replaces the retired central `AI_Questions.md` (archived at `docs/questions/archive-AI_Questions.md`).

- **Change:** map-default-drop-shift (ISSUE — may need a Spec Amendment to `docs/specs/structure-map.md` first)
- **TODO file:** `docs/todo/map-default-drop-shift.md`
- **Spec:** n/a (defect against `docs/specs/structure-map.md` REQ-014 / AC-014)
- **Opened:** 2026-10-09
- **Status:** OPEN  <!-- OPEN | ALL ANSWERED -->
- **Answer rounds:** 0

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

P.2 Interrogate ran 2026-10-09 (18 entries below, all `PENDING`). The five marked `**Blocking:** yes` are the classification, the required rendering, the sequencing against open PR #75, the amendment mechanics, and the still-unrecorded value-triage decision — nothing downstream of them can be decided without an answer.

**Evidence gathered by P.2** (read-only inspection of `feature/structure-map`, PR #75, PR #76):

- `scripts/make_map.py:74` `_DEFAULT_MAX_CHARS = 20`; `:375-386` `_drop_long_defaults` (`args.defaults = [d for d in args.defaults if len(ast.unparse(d)) <= _DEFAULT_MAX_CHARS]`); called from `_signature` at `:396`.
- Spec: REQ-014 (`docs/specs/structure-map.md:287-289`) — "a parameter default is included **only when its unparsed text is ≤ 20 characters**"; AC-014 (`:424`) — "the signature text equals the `ast.unparse` rendering … a parameter default of ≤ 20 characters is shown while a longer one is omitted". No REQ/AC/INV/EDGE anywhere states that the rendered parameter list must stay grammatically valid or call-compatible.
- The rule was chosen in `docs/questions/structure-map.md` **Q-27** ("defaults included when short (≤ 20 chars), omitted otherwise"); the positional-alignment consequence was never asked, so it was never decided.
- **The defect is already live in the committed artifact**, not merely reachable: `tests/mail_test_helpers.py:70` is `simple_template(name='test', subject='Test {{who}}', body_html='<p>Test {{who}}</p>', body_text='Test {{who}}')` (default lengths 6/14/21/14). PR #75's `STRUCTURE.md:1813` renders `simple_template(name: str, subject: str='test', body_html: str='Test {{who}}', body_text: str='Test {{who}}')` — `name` looks required, `body_html`'s default is wrong. AC-021 byte-compares that file.
- Scan of the 895 functions in Packages scope (`src`, `scripts`, `migrations`, `tests/conftest.py`, `tests/*_test_helpers.py`) at PR #75's tree: **exactly one** function has a >20-character positional default (`simple_template`); no function has a single too-long positional default.
- AC-014's unit witnesses do not cover the shift: `tests/unit/test_make_map.py:654 _AC014_LINES` and `:672 _AC014_DEFAULTS` put every long default in `kw_defaults` except `items(pool: list[int]=[1, 2, 3, 4, 5, 6, 7])`, which is its function's **only** default.
- Gates that actually apply to `scripts/make_map.py`: `ruff check .` (lint.yml covers `scripts/`), `uv run mypy scripts/` (REQ-025), the local `structure-map-check` pre-commit hook (REQ-023, `files: \.py$`, check-only), and **no** CI job runs `make_map.py --check` (REQ-023/REQ-026). `complexipy` runs on `src tests` only (`.github/workflows/quality.yml:146`) — the TODO's "complexipy applies to `scripts/`" constraint is inaccurate. PR #76's ruff rule `D` is per-file-ignored for `scripts/*`, so the edited docstring is not D-gated.

## Q-1 — Is the shifted rendering a defect against the approved spec, or behavior the spec never stated?
- **Step:** P.2 Interrogate
- **Blocking:** yes
- **Why needed:** It fixes the change type and therefore the whole phase set. An ISSUE must be "a deviation from approved spec behavior"; if the required behavior is not stated, AGENTS requires a Spec Amendment PR (or reclassification as FEATURE).
- **Context:** Read literally, the current output **satisfies** AC-014: the signature text *is* an `ast.unparse` rendering — of the `ast.arguments` node that `_drop_long_defaults` mutated — and the too-long default *is* omitted. REQ-014 says only "included only when its unparsed text is ≤ 20 characters"; nothing in REQ-014, AC-014, INV-001..006 or EDGE-001..016 requires the rendered parameter list to be valid Python or to mean the same call signature as the source. structure-map Q-27 chose the ≤ 20-char rule without ever considering positional alignment.
- **Question:** Does the approved spec already require a call-compatible signature (→ plain ISSUE, the amendment only clarifies wording), or is "the rendered signature must preserve which parameters have defaults" new behavior the spec never stated (→ Spec Amendment to REQ-014/AC-014 first, or reclassify as FEATURE per the Escalation Rules)? If amended: does it stay inside REQ-014/AC-014, or does it need new IDs (e.g. a new EDGE and/or INV)?
- **Answer:** **PENDING**
- **Date:** 2026-10-09
- **Status:** PENDING
- **Incorporated:** no

## Q-2 — Which rendering is required when a positional default is too long?
- **Step:** P.2 Interrogate
- **Blocking:** yes
- **Why needed:** The fix's whole content, the amended AC-014 wording, and every witness depend on it; the alternatives are not equivalent and one of them is impossible.
- **Context:** `args.defaults` is one list aligned to the **tail** of `posonlyargs + args`, so removing an entry shifts the kept defaults onto earlier parameters; `args.kw_defaults` aligns one-to-one with `kwonlyargs`, so a dropped keyword-only default simply renders with no default (legal). Candidates: **(a)** keep every default in position and abbreviate the long one with a placeholder (`body_html: str=…` or `=...`); **(b)** once any positional default is too long, render **no** positional defaults for that function (`simple_template(name: str, subject: str, body_html: str, body_text: str)`); **(c)** keep today's list-drop and instead document that the map is a simplification, not a call signature; **(d)** something else. Note "drop only the offending entry, keep the others in place" is not expressible — it puts a non-default parameter before defaulted ones, which is invalid Python.
- **Question:** Which of (a)/(b)/(c)/(d) is normative? If a placeholder is used, which token — `…` (the character REQ-017/REQ-018 already use for elision) or `...`? Must the reader be able to tell that a value was abbreviated?
- **Answer:** **PENDING**
- **Date:** 2026-10-09
- **Status:** PENDING
- **Incorporated:** no

## Q-3 — Fix inside open PR #75, or after `structure-map` merges?
- **Step:** P.2 Interrogate
- **Blocking:** yes
- **Why needed:** `scripts/make_map.py` does not exist on `main` — the reproduction test cannot be written, and no RED can be observed, until the code exists. The choice also decides whether `main` ships a wrong signature in the meantime.
- **Context:** The TODO says `Depends on: structure-map (must merge first)` and that "the witness set does not cover this case". The second half is only true of the AC-014 **unit fixture**: the committed `STRUCTURE.md:1813` in PR #75 already exhibits the shift, so the wrong line is inside the artifact AC-021 byte-compares and the local hook checks. PR #75 is otherwise at S6.4 (review report clean, Phase 5 gate passed).
- **Question:** (a) amend PR #75 before it merges so the defect never reaches `main` — but structure-map may not introduce behavior its approved spec does not state, so the spec on `main` would have to be amended first (see Q-4); or (b) merge #75 as-is and fix it afterwards as a separate ISSUE, accepting that `main` carries the misleading `simple_template` signature until then? Which does the user want, and does the answer change the change type (amendment + ISSUE vs amendment + a finding closed inside #75)?
- **Answer:** **PENDING**
- **Date:** 2026-10-09
- **Status:** PENDING
- **Incorporated:** no

## Q-4 — Spec Amendment mechanics, and what the amendment does to open PR #75
- **Step:** P.2 Interrogate
- **Blocking:** yes
- **Why needed:** AGENTS forbids editing an approved spec outside the Spec Amendment Workflow, and the amendment's timing determines whether PR #75's already-GREEN witnesses become stale.
- **Context:** `docs/specs/structure-map.md` is already on `main` (commits `f9e4eea`, `8eb130b`); PR #75's file list does **not** include the spec file. The amendment workflow requires: a new PR, a `## Changelog` v2 entry at the top, identification of affected tasks (any task citing the changed REQ/AC), re-derived tests + RED/GREEN for them, a matrix update, and the spec PR merged **before** implementation resumes. structure-map's T-004 owns AC-014; T-005/T-006 own the committed map (AC-021).
- **Question:** Open the amendment PR now (then PR #75's `_AC014_LINES`/`_AC014_DEFAULTS` witnesses and its committed `STRUCTURE.md` no longer match the amended spec and must be updated on that branch before it merges), or amend only after #75 merges (then the amendment is a normal follow-up PR and this change re-derives its tests)? Which tasks does the user count as "affected tasks" for step 4 of the amendment workflow?
- **Answer:** **PENDING**
- **Date:** 2026-10-09
- **Status:** PENDING
- **Incorporated:** no

## Q-5 — Value-triage decision: implement, merge into another change, or drop?
- **Step:** P.2 Interrogate
- **Blocking:** yes
- **Why needed:** AGENTS prohibits P.4 (branch + worktree) for a TODO whose value-triage decision is not recorded; the TODO's `Decision:` is still `PENDING`.
- **Context:** TODO `## Value triage`: score **2/5**, recommendation "implement — after `structure-map` merges, as a light-tier ISSUE; open the Spec Amendment PR first if the triage shows REQ-014 does not already settle the required rendering". P.2 confirms the rendering is **not** settled by REQ-014 (Q-1) and that the defect is already visible in the committed map, which raises the value above the "currently unwitnessed" premise the score was based on.
- **Question:** Confirm **implement** (and at which point in the #75/#76 order from Q-3/Q-13), or merge this into PR #75, or drop? If the score should be re-rated now that a live witness exists, say so.
- **Answer:** **PENDING**
- **Date:** 2026-10-09
- **Status:** PENDING
- **Incorporated:** no

## Q-6 — Is the "only default of the function" case in scope?
- **Step:** P.2 Interrogate
- **Why needed:** Same root cause, different symptom, and it decides how wide the amended rule and the test set are.
- **Context:** When the too-long default is a function's **only** positional default, the current code renders that parameter as required: `_AC014_LINES` pins `- def \`items(pool: list[int]) -> None\`` for a source parameter `pool: list[int]=[1, 2, 3, 4, 5, 6, 7]`. The map then understates optionality even though nothing shifts. My scan found no such function in the repository today, so this case is real but unwitnessed in the committed map.
- **Question:** Must the fix also keep "this parameter is optional" visible in that case, or is the scope strictly the shift (defaults landing on the wrong parameters)?
- **Answer:** **PENDING**
- **Date:** 2026-10-09
- **Status:** PENDING
- **Incorporated:** no

## Q-7 — Keyword-only and positional-only parameters: same rule or not?
- **Step:** P.2 Interrogate
- **Why needed:** The two branches of `_drop_long_defaults` behave differently today; an amendment that fixes only one leaves a sibling inconsistency, and the fix's size depends on the answer.
- **Context:** `args.kw_defaults` handling (`scripts/make_map.py:383-386`) replaces a long default with `None`, which renders the keyword-only parameter with no default — grammatically valid, but it also hides that the parameter is optional (AC-014's fixture puts all its long defaults here, which is why the witnesses pass). `args.defaults` covers `posonlyargs + args` **jointly**, so a positional-only long default shifts the kept defaults onto earlier parameters exactly like a positional one.
- **Question:** Does the amended rule treat keyword-only and positional-only defaults by the same principle as positional ones (consistent abbreviation), or is "valid but optionality hidden" acceptable for keyword-only parameters? Explicitly: is a positional-only parameter covered by the fix?
- **Answer:** **PENDING**
- **Date:** 2026-10-09
- **Status:** PENDING
- **Incorporated:** no

## Q-8 — Is the 20-character threshold itself open for reconsideration?
- **Step:** P.2 Interrogate
- **Why needed:** The TODO makes the threshold out of scope "unless the triage shows the shift is only reachable through it" — the triage shows exactly that, so the exclusion condition has triggered and needs a decision.
- **Context:** A default is dropped only when its `ast.unparse` text exceeds `_DEFAULT_MAX_CHARS = 20` (`scripts/make_map.py:74`). Raising it to 21 would make the repository's only witness (`simple_template`, 21-char default) disappear from the committed map with a one-line change — but the alignment bug would remain and would return for the next 22-character default. The threshold is a module constant, not a CLI option (REQ-002's six options do not include it).
- **Question:** Keep 20 and fix the alignment (P.2's recommendation), or also revisit the threshold — and is raising the threshold acceptable as *any* part of the fix, or is it suppression and therefore out of scope? Should the threshold become configurable (P.2 recommends no)?
- **Answer:** **PENDING**
- **Date:** 2026-10-09
- **Status:** PENDING
- **Incorporated:** no

## Q-9 — New invariant/edge ID and a property test, or one unit witness?
- **Step:** P.2 Interrogate
- **Why needed:** AGENTS Phase 3 requires a Hypothesis property test for every `INV-XXX`, and Phase 5 requires spec coverage = 100%; whether an INV is created changes the required test set and the light-tier eligibility.
- **Context:** structure-map's `tests/property/test_structure_map.py` witnesses INV-001..006 only. A durable rule would be an invariant of the form "the rendered parameter list parses, and its parameter names, order and which-parameters-have-defaults set match the source signature, except that an over-long default value is abbreviated". The spec's Edge Cases table (EDGE-001..016) has no entry for an over-long default at all.
- **Question:** Does the amendment add an `INV-007` (and an `EDGE-017`) for signature fidelity — in which case a property test over generated signatures is mandatory — or is the rule expressed inside REQ-014/AC-014 with a single unit witness plus the regenerated map?
- **Answer:** **PENDING**
- **Date:** 2026-10-09
- **Status:** PENDING
- **Incorporated:** no

## Q-10 — Reproduction witness: the real committed map line, or a synthetic fixture?
- **Step:** P.2 Interrogate
- **Why needed:** Phase 3 for an ISSUE requires a failing reproduction test; the choice fixes the test category, the traceability row, and whether the test is meaningful before the map is regenerated.
- **Context:** Two candidate witnesses: **(a)** the real one — assert the `simple_template` line in the committed `STRUCTURE.md` (acceptance-level, fails today at PR #75's commit, and is exactly what AC-021 protects); **(b)** a synthetic fixture in `tests/unit/test_make_map.py` next to `_AC014_MODULE` (fast, isolated, but a new fixture rather than the artifact that is actually wrong). Note `tests/mail_test_helpers.py` is itself Packages-scope (REQ-011), so changing that helper would itself change the map.
- **Question:** Which witness — (a), (b), or both — and in which file (`tests/acceptance/test_structure_map.py` vs `tests/unit/test_make_map.py`)? May the reproduction test assert on the committed `STRUCTURE.md` bytes, or must it render into a temp dir?
- **Answer:** **PENDING**
- **Date:** 2026-10-09
- **Status:** PENDING
- **Incorporated:** no

## Q-11 — Are the existing AC-014 witnesses allowed to change?
- **Step:** P.2 Interrogate
- **Why needed:** The no-weakening prohibition and "tests are the contract" both bite here; without an explicit answer the implementing step cannot tell a required re-derivation from a forbidden weakening.
- **Context:** `tests/unit/test_make_map.py:654 _AC014_LINES` pins `- def \`items(pool: list[int]) -> None\`` and `:672 _AC014_DEFAULTS` pins the needle `("[1, 2, 3, 4, 5, 6, 7]", False)` ("21 characters, positional: omitted"). A placeholder-style fix changes both; a drop-all-positional-defaults style changes the `resize(...)` line's rendering of `step`/`exact`. AGENTS forbids weakening or deleting a test to reach GREEN and resolves spec/test conflicts through the amendment, never by editing the test.
- **Question:** Confirm that the amendment authorizes exactly these witness edits as re-derivation from the amended AC-014 (needle replaced, not removed; expected line list rewritten, not loosened), and that no clause of AC-014 may be dropped from the test in the process.
- **Answer:** **PENDING**
- **Date:** 2026-10-09
- **Status:** PENDING
- **Incorporated:** no

## Q-12 — Light-tier ISSUE or full Phase 5?
- **Step:** P.2 Interrogate
- **Why needed:** The light tier changes Phase 5 (targeted + smoke instead of full regression, with the full suite moved to the S6.4 pre-merge gate) and must be qualified in the triage record.
- **Context:** Light tier requires: single feature, ≤ 3 files touched **excluding tests**, no new dependency, no new public interface, no cross-feature change, and existing tests covering the area (named in the triage). Here the touched non-test files are `scripts/make_map.py` and the regenerated `STRUCTURE.md` (required by REQ-021/REQ-027 and the `structure-map-check` hook), plus `docs/specs/structure-map.md` if the amendment is a separate PR. The covering tests are `test_ac_014_symbol_inventory_and_unparsed_signatures` and `test_ac_021_committed_map_matches_fresh_render`.
- **Question:** Does the generated `STRUCTURE.md` count toward the ≤ 3 files, and does the spec file count when it is amended in a separate PR? Is the light tier approved, or full Phase 5 (acceptance + property + contract + coverage + spec coverage 100%)?
- **Answer:** **PENDING**
- **Date:** 2026-10-09
- **Status:** PENDING
- **Incorporated:** no

## Q-13 — Regeneration and merge order across PR #75, PR #76 and this change
- **Step:** P.2 Interrogate
- **Why needed:** Three in-flight changes touch the same generated artifact and the same record files; the order decides who regenerates what and where conflicts land.
- **Context:** PR #75 adds `STRUCTURE.md`, the `structure-map-check` pre-commit hook (`files: \.py$`, check-only) and the map skill. PR #76 (`chore/ruff-d-docstrings`) rewrites docstrings in 40+ `src/` modules — those docstrings **are** the map's summary text — but its file list contains no `STRUCTURE.md`, so once #75 is merged, #76's commits will fail the hook. Both PRs also edit the same record files (`.pre-commit-config.yaml`, `AGENTS.md`, `pyproject.toml`, `docs/verification/traceability.md`, `docs/workflow/PROBLEMS.md`). This ISSUE regenerates the map a third time. REQ-022's rule: on a conflict in `STRUCTURE.md`, take either side and regenerate — never hand-merge.
- **Question:** What merge order does the user want (#75 → #76 → this, or amend #75 first)? Who regenerates `STRUCTURE.md` for #76 — a commit inside #76, or is a separate TODO needed? Should this change be sequenced after both to avoid three map rewrites?
- **Answer:** **PENDING**
- **Date:** 2026-10-09
- **Status:** PENDING
- **Incorporated:** no

## Q-14 — How are the traceability rows written when the IDs collide?
- **Step:** P.2 Interrogate
- **Why needed:** Phase 5 must update the matrix and CI (`scripts/check_traceability.py`) enforces referential integrity; a row that cites a renamed/removed test function fails CI, and an ambiguous row misleads the next change.
- **Context:** `docs/verification/traceability.md` has no spec column, and `REQ-014`/`AC-014` rows already exist for other specs (lines 31, 102, 193, 276, 347) — structure-map's own rows are added by PR #75 (e.g. line 1041 for AC-021) and disambiguated only by the change name inside the Status cell. structure-map's P.5 record (finding 2) notes the checker treats REQ/AC IDs as one global namespace, so a structure-map ID can be "satisfied" by another spec's row.
- **Question:** Should this change add/update rows in the same bare-ID style with `map-default-drop-shift` named inside the cell, and must the new reproduction test's function name be added to the AC-014 row (or to a new amended AC ID)? If the amendment introduces `EDGE-017`/`INV-007`, is a row required for each (the checker fails a defined ID with no row)?
- **Answer:** **PENDING**
- **Date:** 2026-10-09
- **Status:** PENDING
- **Incorporated:** no

## Q-15 — Which quality gates actually apply, and is the TODO's complexipy constraint wrong?
- **Step:** P.2 Interrogate
- **Why needed:** The TODO records a constraint that does not exist; the fix's evidence set must match the real gates, and the after-workflow-optimization reads the TODO.
- **Context:** The TODO says "complexipy `max-complexity-allowed = 15` applies to `scripts/` via the CI job added by structure-map T-001". CI actually runs `uv run complexipy src tests --max-complexity-allowed 15` (`.github/workflows/quality.yml:146`) — `scripts/` is not analyzed, and structure-map Q-28 settled exactly that. What does apply to `scripts/make_map.py`: `ruff check .` (lint.yml covers `scripts/`), `uv run mypy scripts/` (added by REQ-025), and the local `structure-map-check` hook; no CI job runs `make_map.py --check` (REQ-023/REQ-026). PR #76's ruff rule `D` is per-file-ignored for `scripts/*`, so the edited `_drop_long_defaults` docstring is not D-gated.
- **Question:** Confirm the gate set for this change (ruff on changed paths, `mypy scripts/`, targeted tests, full suite at Phase 5 or the S6.4 pre-merge gate). Should the complexipy ceiling be extended to `scripts/` as part of this change (P.2 recommends no — out of scope), and should the TODO's constraint line be corrected?
- **Answer:** **PENDING**
- **Date:** 2026-10-09
- **Status:** PENDING
- **Incorporated:** no

## Q-16 — Is the fix confined to the parameter-default rule, or does it extend to other renderings?
- **Step:** P.2 Interrogate
- **Why needed:** It sets the scope boundary the Phase 6 review checks against, and prevents an unrequested drive-by fix in the same function family.
- **Context:** `_signature` → `_drop_long_defaults` is the only default-shortening path. Adjacent, related-but-different behaviors exist and were deliberately left alone by structure-map S4.3: `_class_name` renders class bases and keyword arguments with **no** length filter at all (`class C(metaclass=SomeVeryLongMetaclass)` renders in full), and it ignores a class's `type_params` (`class G[T](typing.Generic[T])` → `G(typing.Generic[T])`), recorded as "deliberately not changed". NFR-002's ≤ 2 000-line budget is unaffected (the fix changes line content, not line count), as are INV-001 determinism, INV-006 hook cleanliness, REQ-019 and REQ-020.
- **Question:** Is "no behavior change outside the parameter-default rule" the hard boundary — i.e. the class-header rendering and `type_params` stay untouched — or should the same abbreviation rule be applied there too?
- **Answer:** **PENDING**
- **Date:** 2026-10-09
- **Status:** PENDING
- **Incorporated:** no

## Q-17 — Version bump and PR shape
- **Step:** P.2 Interrogate
- **Why needed:** The bump level follows the change type (ISSUE → patch, FEATURE → minor), and the amendment is a separate PR; the base version depends on the merge order, so the shape must be agreed before S6.4.
- **Context:** AGENTS versioning: `bump-my-version bump <level>` at S6.4 with a clean tree, `tag = false`. PR #75 (FEATURE → minor) is still open, so the version this change bumps against depends on Q-3/Q-13. A Spec Amendment PR touching only `docs/specs/` would normally carry no bump.
- **Question:** Is the expected shape "one Spec Amendment PR (no bump) + one ISSUE PR (fix + regenerated map + tests, patch bump)", or does the amendment carry its own bump? If Q-1 lands as FEATURE/reclassification, is the bump then `minor`?
- **Answer:** **PENDING**
- **Date:** 2026-10-09
- **Status:** PENDING
- **Incorporated:** no

## Q-18 — Is any backwards compatibility of map output required?
- **Step:** P.2 Interrogate
- **Why needed:** The fix changes the output of every invocation of the generator; whether an escape hatch is required is a scope decision, not an implementation detail.
- **Context:** REQ-002's six CLI options (`--root`, `--out`, `--check`, `--max-depth`, `--include-private`, `--help`) include nothing controlling the default rule, and REQ-019's determinism guarantee is about repeated runs over an unchanged tree, not about output stability across versions. The only consumer of the output is the committed `STRUCTURE.md` and the agents reading it via the `code-structure-map` skill (advisory only, REQ-026).
- **Question:** Is a compatibility option (a flag preserving the old rendering) or a documented one-time map change required, or is a single regenerated map plus a spec Changelog entry sufficient? P.2 recommends the latter.
- **Answer:** **PENDING**
- **Date:** 2026-10-09
- **Status:** PENDING
- **Incorporated:** no

## Late questions (Phases 2–6)

_none_
