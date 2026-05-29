---
name: update-execution-map
description: Use at session start when planning what's next, after a big task closes, and at session end to record what's queued. Refreshes apps/ms-word/docs/execution-map.md with the next concrete tasks. Triggered when the user says "sırada ne var", "execution map güncelle", or hands off to a new chat.
---

# Update Execution Map

Refresh `apps/ms-word/docs/execution-map.md` so it lists the next
concrete tasks. Future agents land here first to know what to work
on next.

## Process

1. Read the current `execution-map.md` to see what was queued.
2. Listen to the user's stated goals from chat context.
3. Cross-reference `apps/ms-word/docs/architecture/ROADMAP.md`
   for phase order and `apps/ms-word/docs/last-point.md` for
   what's already done.
4. Rewrite the `## Next` section. Update the `Last updated` date.
5. Keep the file under **30 lines**. Concrete tasks only, not
   abstract directions.

## What goes in

- Numbered list of next tasks.
- Per task: one line — name + one-sentence what it does + which UI /
  paint / module layer it touches.
- Concrete acceptance criteria where they exist (e.g. specific hex
  colours, widget names, file paths).
- `## Future` section with the remaining ROADMAP phases as one-liners.

## What does NOT go in

- Process narrative ("we will try X first").
- Long discussion of trade-offs.
- Pros / cons / alternatives.
- Anything that belongs in the commit message of the work itself.

## Trigger checklist

This skill should fire on:

- Session start, if the user mentions "ne yapacağız" or asks for
  current plans.
- Right after a big task closes (merge, ship) — refresh what's left.
- Session end, before handoff to a new chat.
- When the user says "execution map güncelle" / "sırada ne var".

Don't fire on:

- Micro-task transitions inside an ongoing session.
- Brainstorming that isn't yet committed direction — the user has
  to actually agree to a plan before it goes here.
