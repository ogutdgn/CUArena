---
name: commit-style
description: Use before any git commit in cua-bench. Defines subject-line scope tags, staging discipline, and PR-vs-direct-commit guidance.
---

# Commit Style

**Status: SKELETON — refine as we hit edge cases.**

## Subject line

Format: `<scope>: <imperative summary>`

`<scope>` is one of:
- `figma`, `sheets`, `docs` — code or doc changes that are app-specific.
- `verifier` — when changing only the verifier framework of an app, you may also use `figma-verifier`, `sheets-verifier`, etc. for clarity.
- `overview`, `skills`, `repo` — cross-app or repo-root changes.
- `restructure` — large structural changes (rare).
- `fix(<scope>)` — bugfixes; subject is the bug being fixed.
- `feat(<scope>)` — new features; subject is the feature.
- `docs(<scope>)` — documentation-only changes.

Imperative form ("add fillgrad", not "added fillgrad"). Lowercase first word.

## Body

- One blank line after subject.
- Body explains **why**, not what (the diff shows what).
- If the commit ships a feature listed in `feature-checklist.md`, reference the item number: `Ships #16 (Fill with image).`
- If the commit follows from a session, mention the relevant `execution-map.md` entry by date.

## Staging

- Stage files explicitly with named paths. Do not use `git add .` or `git add -A` blanket adds — they pick up generated/local files.
- Verify the diff before committing: `git diff --cached`.
- Never commit `.env`, credentials, raw helper sources, agent log dumps, or `node_modules/.venv` directories.

## When to PR vs commit direct to main

- **Direct to main**: trivial doc fixes, typo corrections, single-file local changes that you've eyeballed.
- **PR**: anything that touches multiple files, restructures folders, changes the log contract, or is hard to review post-hoc as a single diff. Branch name follows `<scope>/<slug>` per `overview/conventions.md`.
- Force-push: only on your own branch, never on main. Don't rebase published branches without coordination.

## What NOT to do

- Skip hooks (`--no-verify`) — investigate the failing hook instead.
- Bypass signing.
- Amend a public commit.
- Lump unrelated changes into one commit "to save time" — split them.
