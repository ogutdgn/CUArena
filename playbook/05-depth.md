# Step 5 — Depth: exhaust what the ranking says matters

## Goal

Full-depth knowledge for **P0–P2** nodes only: every dialog, every option, every state, every
shortcut — documented exactly. P3 gets mid-level treatment; P4 stays at breadth, honestly
labeled. Depth is bought with priority, never spent evenly.

## The depth-endpoint rule (when to stop descending)

Descend **per branch**, independently. UI nests: a dropdown can open another dropdown, a dialog
can open another dialog, on and on. Each newly opened surface has its own set of elements, and
**each element is its own branch** that you follow until it ends.

A branch **ends** when its element **fires an action** on the app/document (a feature) instead
of revealing more UI. A branch **continues** as long as pressing keeps revealing more UI. The
seen-set prevents re-crawling a surface reached by a second path.

Worked example — a dialog with 5 buttons:
- 4 of them open new dialogs → those 4 branches **continue** (recurse into each new dialog and
  repeat the rule there).
- 1 of them triggers a feature → that branch is **done**; its depth is sufficient, nothing more
  to explore down it.
- You do NOT stop the whole dialog because one button ended — you finish the other 4 branches.
  The surface is fully mapped only when **every** element on it has either ended (triggered a
  feature) or been recursed into and mapped.

In data terms: descending = writing `opens` and recursing; endpoint = writing `triggers` and
stopping that branch only.

## How

- For each P0–P2 node: follow its trigger paths through every container; enumerate every child
  element with measured markers; capture per-surface screenshots; recurse per the endpoint rule;
  reset-verify after every press (Step 2's discipline still binds).
- **Full knowledge, not just structure** — for every P0–P2 node AND everything discovered
  beneath it (dialog fields, dropdown entries, options), write the complete rubric into its JSON
  (schema: `design/knowledge-base-design.md`): **what it does**, **how it works/behaves**
  (options, states, defaults, edge cases — measured where possible), **where and how it is
  triggered** (every trigger path, including keyboard shortcuts), **what it affects**, and **what
  it looks like** (screenshot/icon refs). The test: a builder who has never seen the app could
  re-implement this feature from its JSON alone. P0–P2 = documented exactly, to the bottom.
- **Shortcuts**: harvest keyboard shortcuts from element properties, tooltips, menu labels, and
  any in-app shortcut reference — into the shortcut registry (`shortcuts/<keys>.json`,
  context-scoped bindings; schema in the design doc). Depth of shortcut coverage follows node
  priority automatically.
- **Screenshots (mandatory, and verified)**: capture the visual of everything the replica must
  reproduce — every button and its **icon** (cropped), every dialog, panel, and dropdown. For
  P0–P2 controls also record a short visual description. **After each capture, verify it**: the
  agent looks at the image and confirms it actually shows the intended target, not an empty area,
  a wrong window, or a stale frame. Do this fast — a quick glance, not a study — but never skip
  it. (Tool trust from Step 1 already means the capture tool was checked to give correct results
  for buttons/dialogs/dropdowns; this is the per-capture sanity check on top of that.)
- P3 nodes: fill the full rubric + one level of their immediate containers. P4: leave at
  breadth; interiors stay `unexplored`.

## Be sure of

- All common rules (`playbook/README.md`) + Step 2's press/reset discipline.
- Every marker measured; every claim traceable to a journal entry.
- The seen-set: shared dialogs (reachable from several paths) are referenced, not duplicated.

## Proof — the KB's definition of done (from the design doc)

1. Every P0–P2 node has full-depth detail; every P3 node mid-level; P4 breadth-only **by
   design, labeled, not silently missing**.
2. Mechanical completeness passes: every element exactly-one marker; every `opens` resolves;
   every node has a live trigger path; shortcut registry entries all resolve.
3. `overview.md` generated — a human reads it and recognizes the app.
4. The journal reconstructs the whole run; re-running produces the same KB shape.
