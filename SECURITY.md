# Security Policy

## Reporting a vulnerability

Report it through the repository's **Security** tab → *Report a vulnerability*
(GitHub private vulnerability reporting). Do not open a public issue.

No email address is published: the private-reporting form is the only channel.
The form works only once private vulnerability reporting is enabled in the
repository's settings on GitHub — that switch is outside this repository's
contents, so if the *Report a vulnerability* button is missing, the setting has
not been enabled yet.

## Supported versions

| Version | Supported |
|---|---|
| latest release (currently `1.1.0`) | ✅ |
| anything older | ❌ |

Only the latest release is supported. The version in parentheses is a snapshot
of the current release, not part of the rule.

## Response

We aim to **acknowledge** a report within **14 days**. There is **no fix SLA**:
whether and when a fix ships is our call, and a report does not obligate a fix.

## Scope: this is a template, not a service

This repository is a **template / library scaffold**, not a hosted service.
Reports about code you forked or vendored, about the example wiring in
`src/main.py`, or about a deployment you built on top of the template are
**out of scope** — fix those in your own project, and carry your own security
policy.

What is in scope: a vulnerability in the template's own shipped code
(`src/backend/`) or in its default configuration as committed here.

## Current posture (stated as fact, not as a promise)

- The `security` job of `.github/workflows/quality.yml` runs `uv run pip-audit`
  (dependency CVE audit) and `uv run bandit -r src/` (source scan) on pushes to
  `main` and on pull requests targeting `main`.
- The `dependency-review` job runs `actions/dependency-review-action@v5` on pull
  requests only, so a PR that adds a known-vulnerable dependency fails review.
- `.github/dependabot.yml` opens weekly update pull requests for the `uv` and
  `github-actions` ecosystems.
- A real dependency CVE has been fixed through this process — see
  `docs/verification/anyio-cve-fix.md` (PR #48).
