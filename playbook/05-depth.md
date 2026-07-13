# Step 5 — Depth: exhaust what the ranking says matters

## Goal

Full-depth knowledge for **P0–P3** nodes: every dialog, every option, every state, every
shortcut — documented exactly. P4 stays at outline (identity rubric + trigger path + face
screenshot; interiors honest stubs), honestly labeled. Depth is bought with priority, never
spent evenly.

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

- For each P0–P3 node: follow its trigger paths through every container; enumerate every child
  element with measured markers; capture per-surface screenshots; recurse per the endpoint rule;
  reset-verify after every press (Step 2's discipline still binds).
- **Enter the stubs — TRANSITIVELY.** The surfaces left as stubs (`explored: false`) in Steps
  2–3 are exactly what you open now, for P0–P3 nodes: enumerate their real `children[]`, flip
  `explored: true`. And this is **not one level**: when you enter a stub, it almost always
  contains its OWN `opens` elements (a dropdown's "More Colors…" opens a dialog; that dialog's
  "Options…" opens another). Each of those is a new stub, and for a P0–P3 node you must follow
  EVERY one of them, all the way down, until every branch ends at a `triggers` (a fired feature)
  per the endpoint rule. Opening only the node's first surface and stopping is the most common
  depth failure — it looks done but leaves nested stubs behind. **Done for a P0–P3 node = no
  `explored: false` container is reachable from it by ANY chain of `opens`.**
- **Full knowledge, not just structure** — for every P0–P3 node AND everything discovered
  beneath it (dialog fields, dropdown entries, options), write the complete rubric into its JSON
  (schema: `design/knowledge-base-design.md`): **what it does**, **how it works/behaves**
  (options, states, defaults, edge cases — measured where possible), **where and how it is
  triggered** (every trigger path, including keyboard shortcuts), **what it affects**, and **what
  it looks like** (screenshot/icon refs). The test: a builder who has never seen the app could
  re-implement this feature from its JSON alone. P0–P3 = documented exactly, to the bottom.
- **Shortcuts**: harvest keyboard shortcuts from element properties, tooltips, menu labels, and
  any in-app shortcut reference — into the shortcut registry (`shortcuts/<keys>.json`,
  context-scoped bindings; schema in the design doc). Depth of shortcut coverage follows node
  priority automatically.
- **Screenshots (mandatory, and verified)**: capture the visual of everything the replica must
  reproduce — every button and its **icon** (cropped), every dialog, panel, and dropdown. For
  P0–P3 controls also record a short visual description. **After each capture, verify it**: the
  agent looks at the image and confirms it actually shows the intended target, not an empty area,
  a wrong window, or a stale frame. Do this fast — a quick glance, not a study — but never skip
  it. (Tool trust from Step 1 already means the capture tool was checked to give correct results
  for buttons/dialogs/dropdowns; this is the per-capture sanity check on top of that.)
- P4 nodes: leave at outline — identity rubric (from Step 3) + trigger paths + face screenshot;
  interiors stay honest stubs (`unexplored` / `explored: false`).

## Rules

- **R5.1** All common rules (CR1–CR8) + Step 2's press/reset discipline bind. The
  classification rules **R2.3–R2.5** (no effect → no endpoint; ellipsis contract; gallery =
  three zones) bind during every descent exactly as on the skeleton — depth is where their
  violations hide best.
- **R5.2** Every marker measured; every claim traceable to a journal entry.
- **R5.3** The seen-set: shared dialogs (reachable from several paths) are referenced, not
  duplicated.
- **R5.4 Depth walks ELEMENTS, not just containers.** A P0–P3 node is done only when its
  `opens`-chains reach NO `explored:false` container AND NO `unexplored` element (window/scroll
  chrome exempt). "The dialog is explored but half its buttons are `unexplored`" is NOT done —
  an unexplored element never created a container, so a containers-only walk is blind to it.
  [kernel-checked] (LESSONS 2026-07-12: 24 unexplored elements were reachable from P0 nodes in
  a run whose DoD had passed)

## Proof — the KB's definition of done (from the design doc)

1. Every P0–P3 node has full-depth detail; P4 outline-only **by design, labeled, not silently
   missing**.
2. **Transitive-depth check (the one a prior run failed — do it explicitly):** walk `opens`
   from every P0–P3 node through the whole chain; **not one `explored: false` container and not
   one `unexplored` element (chrome exempt) may be reachable** (R5.4). A first-level surface
   opened but its nested "More…/Options…/Special…" dialogs left as stubs = depth NOT done. Your
   DoD checker must compute this reachability at BOTH levels — a containers-only check is blind
   to unexplored elements, and a shallow check will falsely report done.
3. Mechanical completeness passes (`kernel/graph_builder.py`): every element exactly-one
   marker; every `opens` resolves; every node has a live trigger path; every node in a layer;
   no ellipsis-labeled endpoint; shortcut registry entries all resolve.
4. `overview.md` generated — a human reads it and recognizes the app.
5. The journal reconstructs the whole run; re-running produces the same KB shape.
