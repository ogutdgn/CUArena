---
name: update-last-point
description: Use after every commit / branch merge / push to main that lands real work, AND at session end. Refreshes apps/ms-word/docs/last-point.md with what is currently shipped on main. Triggered whenever the user says "session bitti", "last-point güncelle", or anything is squash-merged.
---

# Update Last Point

Refresh `apps/ms-word/docs/last-point.md` so it accurately reflects
what is shipped on `main` right now. Used by future agents to learn
the current state without reading commit history.

## Process

1. Read `git log --oneline -30` to see what has landed on `main`
   recently.
2. Cross-reference `apps/ms-word/docs/architecture/ROADMAP.md`
   for phase context.
3. Rewrite the `## Shipped on \`main\`` and `## Code touchpoints`
   sections. Update the `Last updated` date.
4. Keep the file under **50 lines**. If it grows beyond that,
   compress older bullets into shorter summaries — older phases lose
   detail before newer ones do.

## What goes in

- One bullet per shipped milestone: phase or merged branch.
- Format: `**Name** (commit-hash if merge) — one-line summary of
  user-visible behaviour change.`
- Group by phase or branch.
- Current branch name + working-tree status on a separate line.

## What does NOT go in

- Process narrative ("we tried X, didn't work, then Y").
- Specific code line references.
- Future plans (those live in `execution-map.md`).
- Long explanations of why a decision was made — short.

## Trigger checklist

This skill should fire on:

- After any `git push` to `main` that includes code or doc changes.
- After a squash-merge of a feature branch into `main`.
- When the user says "session bitti" / "kapatıyoruz" / "wrap up".
- When the user asks "neredeyiz" or "ne yaptık" if the doc is
  visibly stale.

Don't fire on:

- Commits that are still on a feature branch (those aren't shipped).
- Doc-only commits that don't change project state.
