# Delete vector point

- **Category:** vector
- **One-line summary:** Remove an anchor point from a vector network while in vector edit mode.

## Triggers
- Select a point (or points) + Delete / Backspace in vector edit mode.
- Cut tool (`X`) — cut a path at a point: different semantic; see note.

## Preconditions
- In vector edit mode.
- One or more anchor points selected.

## Inputs
- Just the trigger.

## Behavior
1. Remove the selected anchor point(s) from the vector's `points` array.
2. Rebind neighboring segments: segments that previously connected to the deleted point connect to each other directly (or break if the removal leaves only one neighbor — creating a dangling endpoint).

## Outputs
- **Scene graph changes:** vector layer's `points` array shrinks; affected segments updated.

## UI feedback
- Canvas: anchor disappears; path reconnects neighbors.

## Side effects
- Undo stack: one entry.

## Related UI schema entries
- `regions/toolbar.md` → secondary-toolbar-vector-edit-mode (Move / Pen selection contexts)

## Semantic event(s) candidate
- `delete_vector_point { layer_id, point_indices: [...], trigger: "delete_key" | "backspace_key" }`

## Source articles
- `edit-vector-layers`

## Notes / gaps
- Cut tool (`X`) is a distinct operation that splits a path at a point rather than removing it. Out of plan/00 §2 explicitly — treat as `visual-only` or flag for later.
- If deleting leaves zero points, the layer may auto-delete (consistent with `commit-text.md` empty-layer cleanup pattern).
