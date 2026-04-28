# Move vector point

- **Category:** vector
- **One-line summary:** Drag an existing anchor point (or handle) to a new position while in vector edit mode.

## Triggers
- Pointer drag on an anchor point while Move (vector-edit) is active.
- Pointer drag on a handle endpoint.
- Arrow keys while a point is selected — nudge by 1 (or 10 with Shift).

## Preconditions
- In vector edit mode.
- Target anchor point or handle is selected (or becomes selected on pointer-down).

## Inputs
- Drag delta OR arrow-key delta.

## Behavior

**Anchor drag:**
1. Update the anchor's position by pointer delta. Handles move with it (unless they are "independent" — handled by `toggle-vector-handle.md`).

**Handle drag:**
1. Move just the handle endpoint. If handles are mirrored, the opposite handle moves mirror-symmetrically.

## Outputs
- **Scene graph changes:** point's `x/y` or `handleIn/handleOut` coordinates updated.

## UI feedback
- Canvas: anchor/handle follows pointer; affected path segments re-render live.

## Side effects
- Undo stack: one entry per committed drag.

## Related UI schema entries
- `regions/toolbar.md` → secondary-toolbar-vector-edit-mode (Move sub-tool)

## Semantic event(s) candidate
- `move_vector_point { layer_id, point_index, target: "anchor" | "handle_in" | "handle_out", from: {x, y}, to: {x, y}, trigger: "drag" | "arrow_key" }`

## Source articles
- `edit-vector-layers`

## Notes / gaps
- None.
