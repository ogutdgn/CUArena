# Step 5 — Depth: exhaust what the ranking says matters

## Goal

Full-depth knowledge for **P0–P2** nodes only: every dialog, every option, every state, every
shortcut — documented exactly. P3 gets mid-level treatment; P4 stays at breadth, honestly
labeled. Depth is bought with priority, never spent evenly.

## The depth-endpoint rule (when to stop descending)

While pressing keeps revealing MORE UI (a dialog inside a dialog, a nested dropdown, a new
section) → keep collecting, with the seen-set preventing re-crawls. The moment an element
**fires an action** on the app/document instead of revealing UI → that is an endpoint: record
the `triggers` marker and stop. In data terms: descending = writing `opens`, endpoint = writing
`triggers`.

## How

- For each P0–P2 node: follow its trigger paths through every container; enumerate every child
  element with measured markers; capture per-surface screenshots; recurse per the endpoint rule;
  reset-verify after every press (Step 2's discipline still binds).
- **Shortcuts**: harvest keyboard shortcuts from element properties, tooltips, menu labels, and
  any in-app shortcut reference — into the shortcut registry (`shortcuts/<keys>.json`,
  context-scoped bindings; schema in the design doc). Depth of shortcut coverage follows node
  priority automatically.
- **Icons/visuals**: for P0–P2 controls, capture icon crops and visual descriptions — the
  replica must render the same control.
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
