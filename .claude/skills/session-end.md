---
name: session-end
description: Use at the end of every development session, before committing. Updates the relevant app's feature-checklist + execution-map, propagates feature ships to verifier task scope, and renumbers waves.
---

# Session End

**Status: ACTIVE for figma; PLACEHOLDER for sheets/docs (pattern carries over once those apps exist).**

## When to run

At the end of any session that shipped or moved code in `apps/<app>/`. Skip if the session was pure research / docs that doesn't ship a feature.

## Steps (per app)

1. **Tick newly-shipped items** in `apps/<app>/app-docs/feature-checklist.md` (`[ ]` → `[x]`).

2. **Update `apps/<app>/app-docs/execution-map.md`**:
   - Add a dated entry at the **top** of the Session log (newest first).
   - Describe what shipped directly — do **not** label entries by Wave number; readers should see what changed, not a wave id.
   - **Delete** completed items from the lower plan. Do not annotate as "Done" — the session log is the record.
   - **Renumber waves from Wave 1** after deletions. The numbering reflects current pending order, not historical.

3. **Propagate to verifier scope**:
   - If a new feature shipped, scan `apps/<app>/verifier/task-docs/tasks.csv` (or equivalent).
   - For each `planned` task whose feature is now implemented: change `Scope` to `in_scope`.
   - If new check primitives are needed (the feature is verifiable in a way no existing check covers), note in the session log; create the primitive in the next session.

4. **Sync mirrors**:
   - If you edited `apps/<app>/CLAUDE.md`, mirror it to `apps/<app>/AGENTS.md`.
   - If you edited the repo-root `CLAUDE.md`, mirror it to repo-root `AGENTS.md`.

5. **Commit per `commit-style` skill.**

## Anti-patterns

- Annotating completed plan items as "✓ Done" instead of deleting them. Two records of the same fact diverge.
- Mixing multiple sessions into one log entry — date stamp every entry distinctly.
- Forgetting to renumber waves after deletion. Stale wave numbers confuse the next session.
