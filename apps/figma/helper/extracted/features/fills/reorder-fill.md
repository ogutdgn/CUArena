# Reorder fill

- **Category:** fills
- **One-line summary:** Change the stacking order of fills on a layer by dragging a fill row's drag handle.

## Triggers
- Hover over the left edge of a fill row → drag handle becomes visible.
- Pointer-down on drag handle + drag vertically to reorder.

## Preconditions
- Selection non-empty.
- Layer has at least 2 fills.

## Inputs
- Pointer drag on the row's drag handle.

## Behavior
1. Drag handle appears on hover (per `guide-to-fills`: "you can hover over the left edge of the fill to reveal the drag handle").
2. Pointer-down + drag moves the row above/below other rows; visual gap indicates the future drop position.
3. Pointer-up commits the new order.
4. Top of the stack in the panel = drawn last (top of paint order).

## Outputs
- **Scene graph changes:** layer's `fills` array reordered to match the new sequence.
- **Selection changes:** none.

## UI feedback
- Drop indicator during drag.
- Canvas re-renders with new fill stacking.

## Side effects
- Undo stack: one entry per reorder commit.

## Related UI schema entries
- `regions/right-properties.md` → fill-section → fill-row drag handle

## Semantic event(s) candidate
- `reorder_fill { layer_ids: [...], from_index, to_index, trigger: "drag" }`

## Source articles
- `guide-to-fills`

## Notes / gaps
- Multi-select reorder: not enumerated by docs. Treat as: same `from`/`to` indices apply to every selected layer (mixed `fills` lengths require fallback — implementer policy).
