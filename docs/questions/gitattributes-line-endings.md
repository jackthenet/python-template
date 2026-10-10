# Questions: gitattributes-line-endings

One question file per change, created at **P.1 Frame** from this template and named `gitattributes-line-endings.md`. It replaces the retired central `AI_Questions.md` (archived at `docs/questions/archive-AI_Questions.md`).

- **Change:** gitattributes-line-endings (DOCS/CHORE)
- **TODO file:** `docs/todo/gitattributes-line-endings.md`
- **Spec:** `docs/specs/gitattributes-line-endings.md`  <!-- or n/a -->
- **Opened:** 2026-10-10
- **Status:** OPEN  <!-- OPEN | ALL ANSWERED — set OPEN by the orchestrator at P.1; ALL ANSWERED once every question in this file has an answer (the orchestrator records it together with the `QUESTIONS-ANSWERED` TODO advance) -->
- **Answer rounds:** 0

Every question that needs user input is recorded HERE — never in a central file. A step that needs input records **all** of its open questions in one batch and returns `BLOCKED-USER`; the orchestrator presents them (as few `ask_user_question` rounds as possible, <= 4 per round, most blocking first), records the answers here, marks each **ANSWERED** and **incorporated**, and relaunches the step **once** with the full answer set. The change is `WAITING` while its questions are unanswered — the orchestrator works on another change meanwhile, it does not idle.

### Entry format

```markdown
## Q-<n> — <short title>
- **Step:** <P.2 Interrogate, or Sx.x <step name> — Phase <n>>
- **Why needed:** <the ambiguity, missing requirement, or decision>
- **Context:** <what the step had learned at the time>
- **Question:** <the question for the user>
- **Recommended:** <the step's proposed answer + one-line reason>
- **Answer:** <the user's answer>  (or **PENDING**)
- **Date:** 2026-10-10
- **Status:** PENDING | ANSWERED
- **Incorporated:** no | yes — <where: REQ-XXX / AC-XXX / spec section / decision>
```

## Preparation questions (P.2)

22 questions, one batch, all `PENDING`. Every claim below is measured on this host (2026-10-10, `main` @ `4e04ed5`, Git 2.51.0.windows.1) — the evidence IDs `E-nn` are defined once in the evidence block and cited by the entries.

### Measured evidence (P.2, this host)

| ID | Command | Output |
|---|---|---|
| E-01 | `git config --list --show-origin \| grep -i crlf`; `git config --get core.safecrlf`; `git config --get core.eol`; `ls .gitattributes` | `file:C:/Program Files/Git/etc/gitconfig  core.autocrlf=true` (system level, not user/repo); `core.safecrlf` unset (exit 1); `core.eol` unset (exit 1); no `.gitattributes` exists |
| E-02 | `git ls-files --eol \| awk '{print $1,$2}' \| sort \| uniq -c` (625 tracked) | `527 i/lf w/crlf`, `55 i/lf w/lf`, `42 i/none w/none`, `1 i/-text w/-text` (the PNG); **0** mixed. The 55 `w/lf` are files tooling wrote after checkout (`docs/todo/*`, `docs/questions/*`, `tests/*/README.md`, …) — the worktree is already inconsistent **across** files. The **index is 100 % normalized** (no `i/crlf`, no `i/mixed`) |
| E-03 | `git cat-file -s :STRUCTURE.md`; `stat -c %s STRUCTURE.md` | blob `146172` B, worktree `148113` B, `1941` CRLF pairs — the TODO's +1 941 figure is confirmed |
| E-04 | `uv run python scripts/make_map.py --check`; `scripts/make_map.py:533`; fresh render vs committed (both CRLF-normalised) | exits **1**, but line 533 is `if _read_bytes(out).replace(b"\r\n", b"\n") != document.encode("utf-8"):` — `--check` **already normalises CRLF**. The content diff is exactly one line: `-docs/ — 225 files (process record)` / `+docs/ — 231 files`; `git ls-files -- docs \| wc -l` → `231` at HEAD |
| E-05 | `uv run pytest tests/acceptance/test_structure_map.py::test_ac_021_committed_map_matches_fresh_render -q` | FAILED with **two independent causes**: `At index 22 diff: b'\r' != b'\n'` (raw-byte compare, test line 1477) **and** `line 452 differs: committed 'docs/ · 225 files' / fresh '231 files'` |
| E-06 | `gh run list --branch main --limit 6`; `gh run view 38027500660 --json jobs` | Quality push runs on `main` **fail** (`38027500660`, `38024929025`, `38021359199`, `38018154840`); job breakdown: `coverage failure`, all other jobs success. So the AC-021 red **is** visible on Linux CI — the TODO's "CI (Linux, LF) never sees it" is false |
| E-07 | scratch clone in a temp dir (`git clone --no-local`, `core.autocrlf=true` inherited): `git status --porcelain \| wc -l` → `0`; write `* text=auto eol=lf`; `git status --porcelain \| wc -l`; `git add --renormalize . && git diff --cached --name-only \| wc -l`; `git check-attr -a STRUCTURE.md` | status stays clean (`1` = the new `.gitattributes` only); **`git add --renormalize .` changes 0 files**; `check-attr` → `text: auto`, `eol: lf`. No phantom diff, no re-normalisation commit needed |
| E-08 | commit the attribute, delete `STRUCTURE.md` + 3 others, `git checkout -- .` | those files become `i/lf w/lf`, worktree size `146172` == blob size. `eol=lf` **wins over** `core.autocrlf=true` on checkout. The other **579** files stay `w/crlf` until they are re-checked-out |
| E-09 | `* text=auto` **without** `eol=lf`, re-checkout; then `git -c core.autocrlf=false checkout -- STRUCTURE.md` | still `i/lf w/crlf`, `148113` B in **both** cases — a set `text` attribute makes checkout follow `core.eol=native` → CRLF on Windows. `text=auto` alone does not fix this host and would force CRLF on a contributor who today gets LF |
| E-10 | `* text eol=lf` (forced `text`, no `auto`), `git add --renormalize .` | **2** files changed, including `src/backend/filemanagement/assets/default_avatar.png`: blob `44ad54c…` → `78909d1…`, `761` → `760` bytes (the PNG contains a `\r\n`). Forced `text` corrupts the binary; `text=auto` leaves it `i/-text`, blob unchanged |
| E-11 | render the map with and without `.gitattributes` present, diff | the render gains exactly one line: `+.gitattributes` (map line 8) — the change **must** regenerate `STRUCTURE.md` |
| E-12 | render from a CRLF worktree vs a fully re-checked-out LF worktree, diff | **0** content diff lines. No gate other than the AC-021 byte comparison depends on checkout endings; `tests/acceptance/test_structure_map.py:104` reads `quality.yml` with `read_text` (universal newlines) |
| E-13 | `git ls-files \| sed 's/.*\.//' \| sort \| uniq -c` | `343 py, 247 md, 19 json, 5 yml, 1 yaml, 1 toml, 1 png, 1 mako, 1 lock, 1 ini, 1 gitkeep, 1 gitignore, 1 editorconfig, 1 LICENSE, 1 migrations/README`. **No** `.bat/.cmd/.ps1/.sh/.ipynb/.svg/.db` is tracked — nothing needs CRLF, and no binary format is untracked-but-plausible in the tree |
| E-14 | overlap check: `grep -rn -i -E "gitattributes\|autocrlf\|line ending\|eol\|renormaliz" docs/specs/ docs/decisions/ docs/verification/`; every TODO in `docs/todo/` (13 live + 17 archived) | only `docs/specs/structure-map.md` (AC-005 last clause, EDGE-016, NFR-007, §13 design note *"Why `--check` normalises newlines instead of adding `.gitattributes`"*), `ADR-085` Alternatives bullet 4 (rejects `*.md text eol=lf`), `docs/verification/structure-map.md` finding 8 + F-07, and `docs/verification/map-default-drop-shift.md` **F-03** — which already records the AC-021 raw-byte CRLF fragility as "a witness-quality ISSUE" candidate, deliberately out of scope there. No TODO other than this one mentions line endings |
| E-15 | `.github/workflows/*.yml` triggers | `lint.yml` PR path filter `src/** tests/** pyproject.toml .pre-commit-config.yaml .github/workflows/lint.yml .github/hooks/**`; `spec-validation.yml` filter `docs/specs/** docs/tasks/** docs/verification/** tests/** src/** scripts/verify_spec.py pyproject.toml`; `quality.yml` **no** path filter. A `.gitattributes` + `STRUCTURE.md` PR therefore runs **only** Quality |
| E-16 | `git worktree list`; `git -C <each worktree> status --porcelain \| wc -l`; `gh pr list --state open` | `main @4e04ed5`, `crosscut/settings-public-registry-setter @3afd407`, `issue/map-default-drop-shift @8215e67`; all three clean (`0`); one open PR: **#80** (map-default-drop-shift PR B, regenerates `STRUCTURE.md`) |
| E-17 | `cat .editorconfig`; `cat .pre-commit-config.yaml` | `.editorconfig` already declares `end_of_line = lf` and `insert_final_newline = true` (advisory only — nothing enforces it on checkout); hooks are `ruff-check`, `ruff-format`, `trailing-whitespace`, `end-of-file-fixer`, `check-yaml`, `check-added-large-files`, `deptry`, `structure-map-check` (`files: \.py$`), `mkdocs-build` — **no** `mixed-line-ending` hook |

## Q-01 — Which EOL policy text goes into `.gitattributes`?
- **Step:** P.2 Interrogate — Phase P
- **Why needed:** The TODO leaves the choice open (`* text=auto eol=lf` vs per-extension rules vs `text eol=crlf` for anything that needs CRLF); the three options produce different checkout results and different risk profiles.
- **Context:** E-02 (index already 100 % LF), E-13 (no `.bat/.cmd/.ps1/.sh` tracked, so nothing genuinely needs CRLF), E-08 (`eol=lf` wins over `core.autocrlf=true`), E-10 (forced `text` corrupts the PNG).
- **Question:** Which rule set: **(A)** `* text=auto eol=lf` (single line, auto-detect binaries); **(B)** a per-extension allowlist (`*.py text eol=lf`, `*.md text eol=lf`, …); **(C)** `* text=auto eol=lf` plus `text eol=crlf` rules for Windows script types that do not exist in this repo?
- **Recommended:** **A** — one line, it is measured to fix the host (E-08), the index needs no re-normalisation (E-07), and C would add rules for file types E-13 shows the repo does not have; B is more lines with strictly less coverage.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-02 — Does the policy mark binaries explicitly, or rely on `text=auto`?
- **Step:** P.2 Interrogate — Phase P
- **Why needed:** `text=auto` decides binary-ness by content sniffing; a mis-detection silently rewrites bytes. The repo has exactly one tracked binary.
- **Context:** E-10 — with `* text eol=lf` (forced `text`) `git add --renormalize` rewrites `src/backend/filemanagement/assets/default_avatar.png` (blob `44ad54c…`→`78909d1…`, 761→760 B). With `text=auto` the PNG stays `i/-text` and its blob is unchanged (E-02, E-07).
- **Question:** Add an explicit binary rule alongside `* text=auto eol=lf` — **(A)** none (trust `text=auto`); **(B)** `*.png binary` only (the one tracked binary); **(C)** a broader binary list (`png/jpg/jpeg/gif/webp/ico/pdf/zip/db`)?
- **Recommended:** **B** — one extra line costs nothing and removes the measured corruption path for the only binary that exists; C marks extensions E-13 shows are not in the tree (YAGNI).
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-03 — Is `eol=lf` mandatory, or is `* text=auto` enough?
- **Step:** P.2 Interrogate — Phase P
- **Why needed:** A reviewer may prefer the shorter `* text=auto`; it does **not** deliver the acceptance signal and actively worsens one contributor case.
- **Context:** E-09 — with `* text=auto` (no `eol`) `STRUCTURE.md` is still `w/crlf` (148 113 B) after a re-checkout, and with `core.autocrlf=false` it is **also** `w/crlf`, because a set `text` attribute makes checkout follow `core.eol=native`.
- **Question:** Confirm the rule must carry `eol=lf` explicitly (and that `* text=auto` alone is rejected)?
- **Recommended:** Yes, carry `eol=lf` — E-09 shows `text=auto` alone leaves the witness red on this host and would flip LF-contributors to CRLF.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-04 — Is a `git add --renormalize .` commit required?
- **Step:** P.2 Interrogate — Phase P
- **Why needed:** The TODO's risk section assumes a mass re-normalisation may be unavoidable; the scope record must state whether the change is one new file or a repo-wide content commit (it changes the diff size, the review burden and the conflict surface).
- **Context:** E-02 (every tracked blob is already LF) and E-07 — in a scratch clone, `git add --renormalize .` after adding `* text=auto eol=lf` produces **0** changed files, and `git status` stays clean.
- **Question:** Confirm the change contains **no** re-normalisation commit (only `.gitattributes` + the regenerated `STRUCTURE.md`, see Q-06)?
- **Recommended:** Confirm no re-normalisation commit — the index is already normalized (E-07), so such a commit would be empty and is exactly the "out of scope" item the TODO lists.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-05 — How is the acceptance signal measured, given existing worktrees keep CRLF?
- **Step:** P.2 Interrogate — Phase P
- **Why needed:** `eol=lf` only affects **future** checkouts; the three live worktrees keep their CRLF files, so "`git ls-files --eol` reports `w/lf`" is false in the worktree the agent is standing in.
- **Context:** E-08 — after committing the attribute, 579 of 583 text files are still `w/crlf`; only the re-checked-out ones became `w/lf`. E-16 — all three worktrees are clean.
- **Question:** How is the signal verified: **(A)** in a throwaway clone under a temp dir (never touching the live worktrees); **(B)** force a re-checkout in the primary worktree (`git rm -r --cached . && git checkout -f .`); **(C)** only assert the attribute exists and leave the worktree state unverified?
- **Recommended:** **A** — it measures exactly what a new contributor gets, is reproducible in the verification record, and cannot disturb the two in-flight changes; B risks the uncommitted state of `main` for no extra evidence.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-06 — Must this change regenerate `STRUCTURE.md`?
- **Step:** P.2 Interrogate — Phase P
- **Why needed:** The map counts tracked files, so adding a root file changes the render; a PR that adds `.gitattributes` without regenerating the map leaves `test_ac_021` red for a new reason. AGENTS.md ties regeneration to `.py` changes, and `.gitattributes` is not `.py`.
- **Context:** E-11 — the render with `.gitattributes` present differs by exactly one added line `+.gitattributes`; E-15 — Quality (which runs the acceptance test) has no path filter, so the PR is checked against it.
- **Question:** Include the regenerated `STRUCTURE.md` in this change (same commit as `.gitattributes`, or a separate `chore: regenerate STRUCTURE.md` commit)?
- **Recommended:** Same commit — the map is stale the moment the attribute is added, and one commit keeps every commit in the PR self-consistent for the AC-021 witness.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-07 — Is the pre-existing map staleness (225 vs 231 docs files) in this change's scope?
- **Step:** P.2 Interrogate — Phase P
- **Why needed:** It is the *other* half of the witness failure and decides whether this change can show a green acceptance signal at all.
- **Context:** E-04/E-05 — the committed map says `docs/ — 225 files`, a fresh render gives `231` (`git ls-files -- docs` = 231 at HEAD); the cause is that direct-to-`main` planning-record commits never regenerate the map. E-06 — this already fails the Quality `coverage` job on `main`. `docs/verification/map-default-drop-shift.md` F-01/F-02 say PR #80's regeneration is what makes it green.
- **Question:** Who absorbs the staleness: **(A)** this change (it regenerates the map anyway per Q-06, so the fix is incidental and free); **(B)** PR #80 only, and this change's PR stays red on AC-021 until #80 merges; **(C)** a separate ISSUE for the regeneration rule?
- **Recommended:** **A** — Q-06 forces a regeneration here anyway, so recording it as an incidental absorption costs nothing and unblocks the signal; C is still worth a TODO later (Q-18).
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-08 — Accept the corrected premise: `--check` already tolerates CRLF
- **Step:** P.2 Interrogate — Phase P
- **Why needed:** The TODO's "Why" states that `make_map.py --check` exits 1 "even when the content is identical". That is false, and the scope record must not be built on it — the CRLF tolerance is a *specified, tested* behavior of this repository.
- **Context:** E-04 — `scripts/make_map.py:533` normalises `\r\n`→`\n` before comparing, and the spec requires it: AC-005 last clause ("**Given** the only difference is that the checked-out file uses CRLF line endings, **Then** it exits `0`"), EDGE-016, NFR-007, witnessed by `test_edge_016_crlf_checkout_is_not_stale`. The current exit 1 is a one-line content diff (E-04).
- **Question:** Confirm the scope record restates the cause as: `--check` is EOL-insensitive by design; the EOL-sensitive gate is **only** `test_ac_021`'s raw-byte comparison (`committed == fresh`, test line 1477), and the `--check` failure is content staleness?
- **Recommended:** Yes — it is measured (E-04/E-05) and it keeps the change from "fixing" a tolerance the spec mandates.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-09 — Does the witness test stay byte-exact?
- **Step:** P.2 Interrogate — Phase P
- **Why needed:** The cheapest way to make `test_ac_021` green locally is to normalise its comparison like `--check` does — that is a test change, which a DOCS/CHORE may not make, and it would remove the very gate this change exists to satisfy.
- **Context:** E-05 (raw-byte compare at line 1477); E-14 — `docs/verification/map-default-drop-shift.md` F-03 already flags this comparison as "a witness-quality ISSUE" candidate and leaves it out of scope; the TODO lists "changing any test to compare line-ending-insensitively" as out of scope because it would weaken the witness.
- **Question:** Confirm the test is **not** touched: neither normalised (weaker) nor deleted, and the F-03 "witness-quality ISSUE" idea stays a separate change?
- **Recommended:** Confirm not touched — with `eol=lf` pinned the byte comparison becomes host-independent, which is the point; normalising it would make the change unverifiable.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-10 — What happens to the stale spec prose (EDGE-016 premise, NFR-007)?
- **Step:** P.2 Interrogate — Phase P
- **Why needed:** `docs/specs/structure-map.md` states as fact that this repository has **no** `.gitattributes`; after this change that parenthetical is false. Editing `docs/specs/` requires the Spec Amendment Workflow, which a DOCS/CHORE cannot do.
- **Context:** E-14 — EDGE-016 ("no `.gitattributes` in this repository, `core.autocrlf=true` on Windows hosts"), NFR-007 ("the checked-out file's line endings may differ"), and §13's design note. The **behavior** those IDs require (`--check` normalises) is unchanged and its witness synthesises CRLF in `tmp_path` (test lines 1258-1279), so it stays green either way.
- **Question:** **(A)** leave the spec untouched (prose goes stale, no normative change); **(B)** open a Spec Amendment PR re-wording EDGE-016/NFR-007; **(C)** leave the spec, record the reversal in a new ADR (Q-11) and note the stale premise in the verification record?
- **Recommended:** **C** — no normative ID changes behavior, so an amendment is ceremony that would also re-open an approved spec; the ADR is where a reversed decision belongs.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-11 — This reverses a recorded decision (ADR-085): new ADR or none?
- **Step:** P.2 Interrogate — Phase P
- **Why needed:** A repo-wide `.gitattributes` is an alternative ADR-085 explicitly **rejected**, and the spec §13 says it is out of scope. Landing it silently leaves the decision record contradicting the repository.
- **Context:** E-14 — `ADR-085` Alternatives bullet 4 ("A repo-wide `.gitattributes` rule (`*.md text eol=lf`) instead of the `--check` normalisation"), spec §13 ("a repo-wide `*.md text eol=lf` rule would change every Markdown file's checkout on Windows and is out of scope"), `docs/verification/structure-map.md` finding 8 and F-07. E-07/E-08 now show the measured cost is zero (index already LF) and the benefit is a host-independent witness.
- **Question:** Record the reversal how: **(A)** new ADR ("`.gitattributes` pins LF in the working tree", superseding ADR-085's rejected alternative, with the E-07/E-08/E-10 measurements); **(B)** amend ADR-085 in place; **(C)** no ADR, CHANGELOG only?
- **Recommended:** **A** — ADRs are append-only decision records and this is a new decision with new evidence; B rewrites history, C leaves the contradiction between ADR-085 and the repo.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-12 — Is DOCS/CHORE still the right type?
- **Step:** P.2 Interrogate — Phase P
- **Why needed:** P.1 classified DOCS/CHORE and asked P.2 to test it. A `.gitattributes` changes what every tool sees on checkout, which is arguably externally observable.
- **Context:** Measured: no `src/`/`tests/` file changes; the index and every blob are unchanged (E-07); the only delta is working-tree bytes for files re-checked-out after the merge (E-08). No approved spec forbids a `.gitattributes` — EDGE-016/NFR-007 only *permit* differing endings, they do not require them. The one thing that would change the type is a test or spec edit (Q-09, Q-10 B).
- **Question:** Confirm **DOCS/CHORE** (configuration, no behavior delta), or reclassify — **ISSUE** if the witness/spec wording is to be fixed here (F-03 in E-14), **FEATURE** if the change must also deliver new checkout capability?
- **Recommended:** Keep **DOCS/CHORE** — measured zero blob/index change and no specified behavior changes; reclassify only if the user wants the AC-021 comparison or the spec prose edited inside this change.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-13 — Does the change touch the machine-level `core.autocrlf=true`?
- **Step:** P.2 Interrogate — Phase P
- **Why needed:** The setting lives in `C:/Program Files/Git/etc/gitconfig` (system-wide, not user, not repo). Touching it is not reproducible for other contributors and is outside the repository.
- **Context:** E-01 (system-level origin, `core.safecrlf`/`core.eol` unset), E-08 (`eol=lf` wins over `autocrlf=true` on checkout — measured, not assumed).
- **Question:** Leave every machine config alone and rely on the committed attribute winning, or also instruct contributors to unset `core.autocrlf`?
- **Recommended:** Leave machine config alone — E-08 proves the attribute wins, and a docs instruction is unverifiable on other hosts and outside the repo's authority.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-14 — What must a contributor with `autocrlf=input` or `false` do?
- **Step:** P.2 Interrogate — Phase P
- **Why needed:** The change's value depends on it being neutral for other configurations; if it were not, the repo would need a contributor migration note.
- **Context:** E-08/E-09 — with `eol=lf` the checkout is LF regardless of `core.autocrlf` (`true` measured; `false`/`input` follow the attribute because it outranks the config); add-time CRLF→LF normalisation is unchanged, so nothing they commit changes.
- **Question:** Confirm no contributor action and no contributor-facing doc migration note is required beyond the CHANGELOG line — or should `userdocs/` gain a short "line endings" page?
- **Recommended:** No contributor action, no new page — the attribute is repo-level and self-enforcing; a page would be prose with no measured audience (E-13 shows one Windows host in this project's evidence).
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-15 — Which CI evidence will this PR actually get?
- **Step:** P.2 Interrogate — Phase P
- **Why needed:** The verification record must state which jobs witnessed the change; a `.gitattributes` + `STRUCTURE.md` PR trips only one workflow's path filters.
- **Context:** E-15 — `lint.yml` and `spec-validation.yml` both path-filter and neither matches `.gitattributes` or `STRUCTURE.md`; `quality.yml` has no filter, and its `coverage` job is the one that runs `pytest tests/ --cov` (E-06 shows that is where AC-021 fails today).
- **Question:** Accept Quality-only CI evidence (with the local Windows measurements in the verification record covering the checkout semantics), or add a path filter / a dedicated job so the attribute itself is CI-witnessed?
- **Recommended:** Accept Quality-only — the `coverage` job runs the witness that matters, and adding filters or jobs is scope creep beyond a DOCS/CHORE (see Q-18).
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-16 — Sequencing against PR #80 and the two in-flight branches
- **Step:** P.2 Interrogate — Phase P
- **Why needed:** PR #80 (`map-default-drop-shift` PR B) regenerates `STRUCTURE.md`; this change regenerates it too and changes checkout semantics for both branches.
- **Context:** E-16 — PR #80 open, all three worktrees clean; E-06 — `main`'s Quality `coverage` job is red now because of the stale map; E-07 — merging this change cannot produce blob-level conflicts (no blob changes), only `STRUCTURE.md` content conflicts (Q-17).
- **Question:** Land this change **(A)** after #80 merges (its regeneration removes the staleness cause, so this PR's map diff is the single `+.gitattributes` line); **(B)** now, in parallel; **(C)** after the `crosscut/settings-public-registry-setter` PR too?
- **Recommended:** **A** — it makes this change's acceptance signal unambiguous (only the EOL cause remains) and minimises the `STRUCTURE.md` conflict; nothing in this change depends on the other two.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-17 — `STRUCTURE.md` conflict handling
- **Step:** P.2 Interrogate — Phase P
- **Why needed:** Both this change and PR #80 regenerate the same generated file, so whichever lands second conflicts on it.
- **Context:** E-11 (this change adds one line to the map), E-16 (PR #80 regenerates it as its main artifact). AGENTS.md already states the rule: never hand-merge the generated file — take either side and regenerate.
- **Question:** Confirm the conflict rule for this change: take either side, then `uv run python scripts/make_map.py` and commit the regenerated map (never a hand-merge), and that the map regeneration is done **last** in the change?
- **Recommended:** Confirm — it is the existing documented rule and the only way a generated file stays truthful.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-18 — Does this change fix the regeneration root cause (no CI `--check` job)?
- **Step:** P.2 Interrogate — Phase P
- **Why needed:** The staleness half of the witness failure (E-04/E-06) recurs every time planning records are committed directly to `main`; the natural "while we're here" fix is a CI job running `make_map.py --check`.
- **Context:** E-04 (docs file count drift), E-06 (`coverage` job red on `main`), E-17 (the `structure-map-check` pre-commit hook fires only on `files: \.py$`, so docs-only commits never check the map). Spec §13 rejected a CI `--check` job: "a CI job for `--check` would fail other changes' PRs on unrelated staleness".
- **Question:** Keep the CI/root-cause fix out of this change (a separate TODO), or add the `--check` job here?
- **Recommended:** Keep it out — it contradicts a recorded spec decision and would red unrelated PRs; open a separate TODO for the regeneration rule instead (pairs with Q-07 C).
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-19 — Rollback procedure
- **Step:** P.2 Interrogate — Phase P
- **Why needed:** The scope record must state how to undo the change, and the honest answer depends on whether the index was rewritten (it was not).
- **Context:** E-07 — `git add --renormalize .` changes 0 files, so no blob or index content is rewritten by this change; E-08 — working-tree endings change only on re-checkout.
- **Question:** Confirm the rollback is a plain `git revert` of the `.gitattributes` commit (+ map regeneration), with no re-normalisation and no data-loss risk, and that worktree endings return to CRLF only on the next re-checkout (harmless either way)?
- **Recommended:** Confirm — measured zero blob churn makes revert complete; anything heavier (filter-repo) is unnecessary and would be a hazard, not a fix.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-20 — Non-goals: confirm the boundary (and one addition)
- **Step:** P.2 Interrogate — Phase P
- **Why needed:** Required scope-boundary question — the TODO's out-of-scope list is short and omits two things a lazy step might be tempted to add.
- **Context:** E-17 (`.editorconfig` already says `end_of_line = lf`; there is no `mixed-line-ending` hook), E-13 (no CRLF-needing file types), E-07 (no re-normalisation needed), E-09 (a `text=auto`-only variant is a worse policy, not a smaller one).
- **Question:** Confirm this change must **NOT**: (1) edit `.editorconfig` or any formatter; (2) add a `mixed-line-ending` pre-commit hook; (3) change any machine/CI git config; (4) rewrite history (`git filter-repo`/BFG) or add a re-normalisation commit; (5) touch any test or `scripts/make_map.py`; (6) edit an approved spec. Anything to add or drop?
- **Recommended:** Confirm all six as non-goals (each is either already satisfied, unmeasurable here, or a witness/spec change that belongs to another change type) — and add nothing further; the in-scope surface stays `.gitattributes` + `STRUCTURE.md` + ADR + CHANGELOG.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-21 — Pre-emptive rules for formats the repo does not have yet?
- **Step:** P.2 Interrogate — Phase P
- **Why needed:** A `.gitattributes` is often written as a long boilerplate list (`*.ipynb text eol=lf`, `*.db binary`, `*.lock -diff`, `linguist-generated`); each rule is a promise about a file that does not exist.
- **Context:** E-13 — the tracked extension census has no `.ipynb`, `.svg`, `.db`, `.bat`, `.ps1`, `.sh`; `uv.lock` is already LF in the index (E-02); E-02 shows the 42 `i/none` files (empty `__init__.py`, `.gitkeep`) are untouched by an `eol` rule.
- **Question:** Keep the file minimal (Q-01 A + Q-02 B) or seed the boilerplate list for future formats?
- **Recommended:** Minimal — every extra rule is untestable today, and the measured hazards (E-10) come from over-broad `text` rules, not under-broad ones.
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

## Q-22 — Where does the policy get documented for future agents?
- **Step:** P.2 Interrogate — Phase P
- **Why needed:** Phase 6 step 9 records reusable shared capabilities in `AGENTS.md`, but that check is FEATURE/CROSS-CUTTING only; a DOCS/CHORE that changes checkout semantics still needs a place future changes read.
- **Context:** E-14 (ADR-085 and spec §13 currently say the opposite), E-15 (CHANGELOG is required for every change type), AGENTS.md has no line-endings section today.
- **Question:** Documentation surface: **(A)** ADR + `CHANGELOG.md` only; **(B)** plus a short `AGENTS.md` note (e.g. under Tooling) that the repo pins LF via `.gitattributes` and that `--check` stays CRLF-tolerant; **(C)** plus a `userdocs/` page?
- **Recommended:** **B** — the ADR records the decision, but agents editing `STRUCTURE.md`/witnesses need the one-line invariant where they already read the tooling rules; C has no audience (Q-14).
- **Answer:** **PENDING**
- **Date:** 2026-10-10
- **Status:** PENDING
- **Incorporated:** no

### Category coverage

| Category | Result |
|---|---|
| Scope & Goals / Non-goals | covered (Q-01, Q-07, Q-18, Q-20, Q-21) |
| Data & State (files, endings, binaries) | covered (Q-01, Q-02, Q-03, Q-04; E-02, E-10, E-13) |
| Behavior & Edge Cases (checkout, worktree state, mixed endings) | covered (Q-03, Q-05, Q-19; E-08, E-09) |
| Interfaces & Contracts (spec IDs, witness test, generated map) | covered (Q-06, Q-09, Q-10; E-04, E-11, E-14) |
| Constraints & Risks (machine config, CI config, rollback) | covered (Q-13, Q-14, Q-15, Q-19; E-01, E-15) |
| Testing & Acceptance (is the signal achievable?) | covered (Q-05, Q-07, Q-08, Q-09, Q-15; E-04, E-05, E-06) |
| Architecture & Conventions (reversed decision, docs surface) | covered (Q-11, Q-12, Q-22; E-14, E-17) |
| Sequencing & Collisions (in-flight PRs/branches) | covered (Q-16, Q-17; E-16) |
| Overlap with existing specs and every TODO | covered (E-14 — no overlapping TODO live or archived; the nearest record is `map-default-drop-shift` F-03, which defers the witness-quality fix; no question needed because there is no double work to choose between) |
| Performance / runtime budget | skipped — the change adds no runtime code path; the only cost is one attribute lookup per checkout (E-12 shows the render itself is EOL-independent) |
| Security / secrets | skipped — no secret, credential or trust boundary is involved; the attribute only selects newline bytes (E-07: zero blob churn) |

## Late questions (Phases 2–6)

<questions discovered after the change entered the workflow; same entry format, Step field set to the step that found it>
