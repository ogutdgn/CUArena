# Drop layer out of frame

- **Category:** frames
- **One-line summary:** Drag a child outside its parent frame's bounds and release; the child detaches from its parent (becomes a top-level layer or moves to a different parent).

## Triggers
- Pointer drag of a layer that's a child of a frame.
- Drag path takes the layer outside the parent frame's bounds.

## Preconditions
- The dragged layer has a non-page parent (i.e. is a child of a frame, group, or component).

## Inputs
- Pointer drag.
- Optional `Space bar` modifier — keep the layer in its current parent regardless of position (per `parent-child-and-sibling-relationships`).

## Behavior
1. As the user drags out of the parent's bounds:
   - If the layer's bbox no longer overlaps the parent past the threshold (50% in mock per commits `4413ce0` / `74c4896`), reparent live to the next valid parent (which may be the page root, an outer frame, etc.).
   - If `Space` is held, parent stays unchanged.
2. On release, the final parent is whichever was active at release.

## Outputs
- **Scene graph changes:** `parent_id` updates; coordinates convert to new parent's local space.
- **Selection changes:** none (still on the moving layer).

## UI feedback
- Parent-bounds dashed overlay on whatever frame is the current candidate parent.
- Layers panel reflects new nesting.

## Side effects
- Undo stack: one entry covering the drag's final state.

## Related UI schema entries
- `regions/canvas-overlays.md` → parent-bounds-overlay, selection-bounding-box

## Semantic event(s) candidate
- `reparent_layer { layer_id, from_parent_id, to_parent_id | null, trigger: "canvas_drag", modifiers: { space } }`

## Source articles
- `parent-child-and-sibling-relationships`
- `frames-in-figma-design`

## Notes / gaps
- This and `reparent-via-canvas-drag.md` describe the same mechanism in opposite directions; combine into one engine op.
