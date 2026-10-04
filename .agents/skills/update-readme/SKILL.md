---
name: update-readme
description: "Updates the project's README.md to current GitHub front-page practice: inspect the repo first (README, pyproject.toml, LICENSE, .github/workflows/, git remote), add a badge row only for things that really exist, lay the page out in the 8-section order skipping what does not apply, keep every command copy-pasteable and every relative link resolving, and report what changed plus anything unverifiable. Use when README.md needs a refresh, when a badge or command in it is stale or wrong, and when a new tool, workflow or feature must become visible on the front page."
---

# Task: Update the GitHub README

Improve the project's `README.md` so it follows current best practices and includes accurate status badges.

## 1. Inspect first (don't guess)
- Read the existing README, `pyproject.toml` / `package.json` (or equivalent), `LICENSE`, `.github/workflows/`, and the git remote URL.
- Determine the real project name, description, supported language versions, license, package registry (if published), and CI setup.

## 2. Badges
- Add a single row of badges directly under the title.
- Only include badges that match something that actually exists in the repo, e.g.:
  - CI status (the actual workflow file name)
  - License
  - Supported language versions
  - Package version/downloads (only if published)
  - Code coverage (only if configured)
  - Code style/tooling (e.g. Ruff, uv, pre-commit) if used
- Use shields.io or the native GitHub workflow badge, with the correct `owner/repo`. Never invent URLs or badges for services the project doesn't use.
- Each badge needs alt text and should link to the relevant page.

## 3. Structure and content
Use this order, skipping sections that don't apply:
1. Title + badges + one-sentence description
2. Features / why this exists
3. Installation
4. Quick start / usage (a minimal, working example)
5. Configuration
6. Development (setup, tests, linting, how to run checks)
7. Contributing
8. License

## 4. Quality rules
- Preserve all accurate existing information; don't delete content without a reason.
- Every command and code snippet must be copy-pasteable and match the project's real tooling.
- Use fenced code blocks with language tags, relative links for in-repo files, and consistent heading levels (a single H1).
- Keep it scannable: short paragraphs, no filler or marketing fluff.
- Add a table of contents only if the README is long.

## 5. Output
- Edit `README.md` in place.
- Afterwards, list what changed and flag anything you couldn't verify (e.g. a badge whose service isn't configured yet).

## Repo protocol

Make the edit in the **change worktree**: `README.md` reaches `main` only through the merged PR, never as a direct commit to `main`.
The "list what changed and flag anything you couldn't verify" output is the change's report — record it in the change's `docs/verification/<name>.md`, not only in a chat reply.
