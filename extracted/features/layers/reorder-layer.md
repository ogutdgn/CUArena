# Reorder layer (z-index / panel order)

- **Category:** layers
- **One-line summary:** Change a layer's position within its parent's children list (z-order on canvas / row order in the Layers panel).

## Triggers
- Drag-drop a layer row in the Layers panel to a new position.
- Keyboard:
  - `Cmd ]` (Mac) / `Ctrl ]` (Win) — bring forward (one step up in order)
  - `Cmd [` / `Ctrl [` — send backward (one step down)
  - `Cmd Alt ]` — bring to front (top of parent's children)
  - `Cmd Alt [` — send to back (bottom)
- Right-click → Arrange → Bring forward / Send backward / Bring to front / Send to back.

## Preconditions
- Selection is non-empty.

## Inputs
- For drag: pointer-down on a row, drag, pointer-up at a new position.
- For keyboard / menu: trigger only.

## Behavior

**Panel drag:**
1. Pointer-down on a row: that row becomes the drag target.
2. During drag: visual drop indicator shows where the row would land — before a sibling, inside a frame (if hovered on a container row), after a sibling.
3. Pointer-up: reparent / reorder accordingly.

**Shortcut / menu:**
- Bring forward: swap with next sibling (higher z).
- Send backward: swap with previous sibling.
- Bring to front: move to end of parent's children.
- Send to back: move to start.

## Outputs
- **Scene graph changes:** selected layer's position in its parent's `children` array changes (or parent itself changes if drag moves it into a different container).
- **Selection changes:** none.

## UI feedback
- Canvas: z-order visually updates (overlapping layers re-stack).
- Left panel: row position updates.

## Side effects
- Undo stack: one entry per commit.

## Related UI schema entries
- `regions/left-navigation.md` → layers-tree
- `regions/floating-overlays.md` → right-click-context-menu

## Semantic event(s) candidate
- `reorder_layer { layer_id, from_parent_id, from_index, to_parent_id, to_index, trigger: "panel_drag" | "shortcut_bring_forward" | "shortcut_send_backward" | "shortcut_bring_to_front" | "shortcut_send_to_back" | "context_menu" }`

## Source articles
- `parent-child-and-sibling-relationships`
- `select-layers-and-objects`

## Notes / gaps
- Reparenting via panel drag (dropping into a different container): handled by the same event with `from_parent_id ≠ to_parent_id`. Distinct from pure reorder.
