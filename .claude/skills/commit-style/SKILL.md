---
name: commit-style
description: Use before any git commit in cua-bench. Defines subject-line scope tags, body detail requirements, staging discipline, and PR-vs-direct-commit guidance.
---

# Commit Style

## Subject line

Format: `<type>(<scope>): <imperative summary>`

`<scope>` is one of:
- `figma`, `sheets`, `docs`, `libreoffice` — app-specific code or doc changes.
- `figma-verifier`, `sheets-verifier` etc. — verifier-only changes (libreoffice has no verifier yet).
- `overview`, `skills`, `repo` — cross-app or repo-root changes.
- `restructure` — large structural changes (rare).

`<type>` is one of:
- `feat` — new user-visible feature or capability.
- `fix` — bug fix (subject names the bug, not the solution).
- `refactor` — internal restructure with no behaviour change.
- `ui` — visual-only change (no logic, no semantic events).
- `docs` — documentation only.
- `test` — verifier or QA scripts only.
- `chore` — tooling, deps, config.

Imperative form, lowercase first word. Keep under 72 chars.

## Body — required for all non-trivial commits

Always include a body. One blank line after the subject, then:

**What changed** — bullet list of concrete changes (files/components/behaviour). Be specific: name the components, functions, or files touched. Example:
```
- Remove LeftRail component and its grid column from App.tsx
- Pages section: add collapse toggle; show active page name when collapsed
- Add SearchPanel: layer + page search, scope dropdown (this page / all pages),
  result grouping by page in all-pages mode, highlighted match text
- Remove --left-rail-width from tokens.ts and global.css
```

**Why** — one or two sentences explaining the motivation. What problem does this solve, or what goal does it serve?

**Impact notes** (include when relevant):
- `Logger impact: none` — or describe what semantic events changed.
- `Verifier impact: none` — or describe what checks are affected.
- `Breaking: <what>` — if any data-id, API, or log contract changed.

If the commit ships a feature in `feature-checklist.md`: `Ships #N (feature name).`

## Trailer

**Do NOT add `Co-Authored-By: Claude` or any AI authorship trailer.** Never.

## Staging

- Stage files explicitly by path — never `git add .` or `git add -A`.
- Run `git diff --cached --stat` before committing to verify the staged set.
- Never commit: `.env`, credentials, `node_modules/`, `.venv/`, raw helper sources, agent log dumps, `dist-*`, `*.tsbuildinfo`, `package-lock.json` (unless deps actually changed intentionally).

## When to PR vs commit direct to branch

- **Direct commit**: single-concern change on a feature branch, already reviewed in conversation.
- **PR**: anything touching the log contract, verifier framework, or 5+ files — create a PR so it can be reviewed before merging to main.
- Force-push only on your own branch, never on main.

## What NOT to do

- Skip hooks (`--no-verify`) — investigate the failing hook.
- Bypass signing.
- Amend a published commit.
- Lump unrelated changes into one commit.
