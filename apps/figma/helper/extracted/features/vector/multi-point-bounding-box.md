# Multi-point bounding box editing

- **Category:** vector
- **One-line summary:** When multiple vector points are selected in vector edit mode, a bounding box appears that lets you resize / move / rotate the selected points as a group.

## Triggers
- Vector edit mode active.
- 2+ vector points selected (via Lasso, Shift-click, or marquee).

## Preconditions
- Vector edit mode active.
- Multi-point selection.

## Inputs
- Pointer drag on bbox handles (corners / edges).
- Modifiers:
  - **`Shift`** during corner drag — resize proportionally.
  - **`Option` / `Alt`** during drag — resize from center.
  - **`Shift`** while rotating from a corner — 15° increments.
  - **`Space`** held during another action — temporarily switches to reposition the points.

## Behavior
1. Bounding box renders around selected points (not the whole layer).
2. Drag a side: scale points along that axis (rest of the network unchanged).
3. Drag a corner: scale 2D.
4. Hover near a corner outside the bbox: rotate cursor → drag to rotate.
5. With `Space` held mid-drag, can reposition the points while keeping the action context.

## Outputs
- **Scene graph changes:** selected points' positions / handles updated.
- **Selection changes:** sub-selection retained.

## UI feedback
- Bounding box renders around selected points.
- Cursor changes per affordance (resize / rotate / reposition).

## Side effects
- Undo stack: one entry per drag commit.

## Related UI schema entries
- `regions/canvas-overlays.md` → vector-multipoint-bounding-box

## Semantic event(s) candidate
- `transform_vector_points { layer_id, point_indices: [...], operation: "resize" | "rotate" | "translate", from, to, modifiers, trigger }`

## Source articles
- `edit-vector-layers`

## Notes / gaps
- Excellent precision tool for vector cleanup; documented at length in the source article.
