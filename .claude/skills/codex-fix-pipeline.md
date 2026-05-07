---
name: codex-fix-pipeline
description: Use when starting bug-fix or feature-development work in cua-bench (the user reports a bug, asks for a fix or new feature, runs an audit, or says "let's pipeline this"). Drives the audit → file → plan → codex-review → implement → codex-review → commit → push flow that this repo has settled on. Skip only if the user explicitly says "one-off, no full pipeline".
---

# Codex Fix Pipeline (cua-bench)

**Status: ACTIVE.** Refined across two real sessions (8 bug fixes + 1 feature add for the figma mock); the steps below reflect what actually held up under Codex review and per-bug commits.

The pipeline is the same for bug fixes and for new features. It builds on:
- `codex:codex-rescue` subagent for plan / diagnosis review.
- `codex-companion.mjs review` for diff review on the working tree.
- `apps/<app>/app-docs/mock_improvement_steps.md` as the per-app open/closed audit log (bug fixes + UI improvements + feature updates, single numbering across all three).

## When to invoke

Trigger on:
- "bug bulduk", "şu kırık", "fix this", "audit"
- "feature ekle", "implement X", "build the Y feature"
- A reply that lists symptoms from a manual run-through of tasks.
- Receiving a Codex audit report.

Skip on:
- One-line tweaks (typo, rename a constant) where the full pipeline would be heavier than the diff.
- The user explicitly waiving it: "skip the pipeline this time".

## Step 0 — File the bug / gap

If the user reports symptoms, normalize them into `apps/<app>/app-docs/mock_improvement_steps.md`:

- The doc has three sections: `## Bug fixes`, `## UI improvements`, `## Feature updates`. File each item under the right one.
- Heading inside a section: `#### N. 🔴 P? — <one-line title>` for bugs, `#### N. 🔴 — <title>` for UI/features (no P-priority for those; ordering is by user request and safe-first execution).
- Status legend in the doc header: `✅ Fixed` / `🟢 Shipped` / `🔴 Open` / `🟡 In progress` / `⚪ Wontfix`.
- Bug priority: P1 = wrong final document state / undo corruption / runtime crash. P2 = log-stream contract break / missed semantic event / recoverable misbehavior. P3 = forensic, UX, doc-rot.
- Per item: short root-cause hypothesis (bugs) or expected behavior (features/UI), file paths (best guess), expected vs actual, optional repro.
- Item numbers are continuous across all three sections (single sequence preserves stable `#N` references in commits).

Audits ingested verbatim from Codex go in their own dated section so the pipeline source is auditable.

## Step 1 — Plan

Read every file the bug list points at (parallel `Read`s). Write a per-item plan covering:

- **Root cause** (verified in code, not just hypothesized).
- **Approach** (concrete: which function, what's added/changed).
- **Files** (exact paths).
- **Risk / regressions** to watch.
- **Execution order** for the batch (smallest/safest first; items that other fixes depend on, last).

Don't dispatch Codex with a vague plan — Codex's review is only as useful as the plan's specificity.

## Step 2 — Codex plan review (mandatory)

Use `Agent` with `subagent_type: codex:codex-rescue`. Foreground (no `--background`). Standard prompt skeleton:

```
Review the following plan for N items. For each: (a) root cause correct?
(b) approach sound? (c) edge cases / regressions missed? (d) better
approach? Read <list the affected files>. Top with a "BLOCKERS" section
if anything must change before I implement.

The constraint: <any hard rule like "preserve pen vs pencil attribution
in the log">

# Plan
<paste the plan>

--wait --fresh --model gpt-5.5
```

Codex returns BLOCKERS + per-item review. Accept all BLOCKERS unless they'd violate a user-stated hard rule. Note ek-iyileştirmeler (refactor suggestions, missed cases) and fold them into the implementation pass. Don't loop the plan — accept and proceed.

## Step 3 — Implement

Order from Codex's accepted plan. After each fix:

- Run `npm run typecheck` from `apps/<app>/mock/` (TS apps).
- Run `apps/<app>/.venv/Scripts/python apps/<app>/scripts/qa_verifiers.py` if the app has a verifier QA harness — it must stay 50/50 OK on figma.
- Don't continue to the next item until the current one typechecks AND the QA passes.

## Step 4 — Codex diff review (mandatory, iterate)

After all fixes (or after each, if scope is large), run:

```bash
MSYS_NO_PATHCONV=1 node "C:/Users/ogutd/.claude/plugins/cache/openai-codex/codex/1.0.4/scripts/codex-companion.mjs" review --wait --scope working-tree
```

(`MSYS_NO_PATHCONV=1` is required from Git Bash so taskkill flags survive path translation.)

Codex returns review comments (P1/P2/P3 + file:line). Address every P2+ comment in code, re-run typecheck/QA, then re-run review. Loop until Codex returns "no clear functional regression" or only flags untracked files (`last-point.md`, `task-qa.md`) that are out of scope. 4 rounds is normal for a feature; ≤2 for bug-only batches.

Don't ship past a P2 comment by hand-waving — re-implement.

## Step 5 — Per-bug commits

Convention from `commit-style.md` plus user standing rules:

- One commit per item — even if files overlap. Split intermixed files via temporary `git checkout HEAD -- <file>` + `Edit` to apply only the current item's hunks, commit, then `Edit` again for the next item.
- Subject: `fix(<scope>): <imperative summary> (#N)` or `feat(<scope>): <feature> (#N)` where `#N` matches `mock_improvement_steps.md`.
- Body: 1–3 sentences explaining **why**, not what. Mention root cause + chosen fix path + any non-obvious tradeoff.
- **No** `Co-Authored-By: Claude` trailer (user explicit standing instruction).
- After the last fix: a single `docs(<scope>): mark bugs #N–M as fixed and link commit refs` commit that updates `mock_improvement_steps.md` ✅ + commit SHA + one-line summary per item.

Match scope tags from `commit-style.md` (`figma-mock`, `figma-verifiers`, etc.).

## Step 6 — Branch & push

- Never push directly to `main` — repo enforces PR-review convention.
- Branch name: `<scope>/<short-slug>` (e.g. `fix/figma-mock-audit-fixes`).
- If commits accidentally landed on local `main`: `git checkout -b <new-branch>` to carry them, then `git branch -f main origin/main` to reset the local main pointer.
- **Always ask the user before `git push`.** They merge via PR on GitHub.

## Standing rules to inherit (do not re-litigate)

- `apps/<app>/delivery-1/` is generally frozen. Verifier corrections that affect score correctness ARE allowed when discussed first, and each delivery-1 modification is logged at repo-root `delivery-1_updates.md` (file-by-file, with reasoning).
- Mock event emission preserves tool attribution — pen and pencil emit separate semantic events; never collapse them into a generic event.
- For the figma mock specifically: every meaningful document mutation must (a) go through `engine/dispatch.ts`, (b) emit a semantic event matching the schema, (c) be undoable. New properties or features that bypass any of those are P2 bugs.
- Commit messages stay terse. The pipeline's value is in the diff and `mock_improvement_steps.md`, not in commit prose.

## Output behavior

- TodoWrite for the run: one item per pipeline step.
- After commits: a tight summary table (commit SHA, scope, one-line). Then ask "push edeyim mi?".
- Don't summarize each fix in chat — the user can read `git log` and `mock_improvement_steps.md`.
