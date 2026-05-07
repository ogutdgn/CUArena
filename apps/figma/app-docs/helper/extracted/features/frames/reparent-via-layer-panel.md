# Reparent via Layers panel drag

- **Category:** frames
- **One-line summary:** Drag a layer's row in the Layers panel into a different parent (frame, group, or top level) to reparent it.

## Triggers
- Pointer drag on a row in the Layers panel into another row's body or onto the gap between rows.

## Preconditions
- Layers panel visible.
- Source layer not locked.

## Inputs
- Pointer drag with a drop indicator showing the candidate target (between siblings = sibling drop; on a frame row body = drop-into-frame).

## Behavior
1. On pointer-down on a layer row, drag begins.
2. Drop indicator (a horizontal line or row highlight) shows the candidate insertion point.
3. Hovering over a frame/group row body marks "drop into" — release reparents into that frame.
4. Hovering between sibling rows marks "drop between" — release reorders the layer at that index.
5. On release, parent and z-order update accordingly.
6. Cross-parent drag is supported (matches commit `fe7b4c2`).
7. Locked layers cannot be dragged (covered by `lock-and-unlock-layers`).

## Outputs
- **Scene graph changes:** layer's `parent_id` and z-index update; coordinates convert to new parent's local space.
- **Selection changes:** none (the dragged layer remains selected).

## UI feedback
- Drop indicator during drag.
- Panel rows reorder on drop.
- Canvas re-renders if z-order changes affect compositing.

## Side effects
- Undo stack: one entry per panel-drag commit.

## Related UI schema entries
- `regions/left-navigation.md` → layers-tree (drag-drop)

## Semantic event(s) candidate
- `reparent_layer { layer_id, from_parent_id, to_parent_id, from_z_index, to_z_index, trigger: "layer_panel_drag" }`

## Source articles
- `view-layers-and-pages-in-the-left-sidebar`
- `parent-child-and-sibling-relationships`

## Notes / gaps
- Visual scroll behavior of the panel (auto-scroll near top/bottom edges during drag) not pinned by docs.
- Multi-row drag: selection of multiple rows can be dragged together (per Figma convention) — keep all selected layers' relative order.
